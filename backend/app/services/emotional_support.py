"""Capa de apoyo emocional y seguridad del chat.

Es un módulo basado en reglas, determinista y sin dependencias externas. Corre ANTES
de cualquier modelo (hoy el clasificador de intenciones; mañana un LLM local) porque en
los temas sensibles la respuesta no puede depender de un modelo probabilístico:

1. Detección de crisis (ideación suicida / autolesión): respuesta fija, cálida y con
   recursos reales. Nunca valida el deseo de morir ni minimiza.
2. Ejercicios de bienestar (respiración, anclaje 5-4-3-2-1, desahogo, dividir tareas).
3. Detección de emociones con negación e intensidad ("no estoy triste", "muy ansioso").

NO es un servicio clínico ni sustituye a un profesional.
Recursos para Colombia: Línea 106 (salud mental) y 123 (emergencias).
"""
from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

LINEA_106 = "Línea 106 (salud mental, gratuita, 24 horas)"
EMERGENCIAS = "123"


# ---------------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------------
def normalize(text: str) -> str:
    """Minúsculas, sin tildes ni eñes, solo letras/números/espacios."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s,.;!?\-]", " ", text)).strip()


NEGATORS = {"no", "nunca", "jamas", "tampoco", "ni"}
INTENSIFIERS = {"muy": 1.5, "demasiado": 1.6, "super": 1.5, "tan": 1.4, "bastante": 1.3,
                "re": 1.3, "mucho": 1.4, "extremadamente": 1.8, "totalmente": 1.5,
                "completamente": 1.5}
DIMINISHERS = {"poco": 0.6, "algo": 0.7, "ligeramente": 0.6, "medio": 0.7}


def _negated_before(text: str, index: int, window: int = 14) -> bool:
    return bool(re.search(r"\b(no|nunca|jamas|tampoco|ni)\b", text[max(0, index - window):index]))


# ---------------------------------------------------------------------------
# 1. Crisis
# ---------------------------------------------------------------------------
_CRISIS_PATTERNS = [
    r"\b(me )?quiero morir(me)?\b", r"\bquisiera morir(me)?\b", r"\bganas de morir(me)?\b",
    r"\bmatarme\b", r"\bmatarse\b", r"\bme voy a matar\b", r"\bme quiero matar\b", r"\bsuicid",
    r"\b(quitarme|quitarse) la vida\b", r"\bacabar con mi vida\b", r"\bterminar con mi vida\b",
    r"\bacabar con todo\b", r"\bno quiero (seguir )?(vivir|viviendo)\b", r"\bya no quiero (estar )?vivo\b",
    r"\bno vale la pena (seguir )?vivir\b", r"\bhacerme dano\b", r"\blastimarme\b", r"\bcortarme\b",
    r"\bmejor (estar )?muerto\b", r"\bseria mejor no (estar|existir)\b", r"\bmejor sin mi\b",
    r"\bdesaparecer para siempre\b", r"\bno quiero despertar\b", r"\bpensando en morir\b",
]
_CRISIS_RE = [re.compile(p) for p in _CRISIS_PATTERNS]
_HIGH_RISK_RE = re.compile(
    r"\b(me voy a matar|tengo un plan|esta noche|ya (tome|me tome)|las pastillas|tengo las pastillas|"
    r"lo voy a hacer|ya lo decidi|me voy a quitar la vida|me quiero matar ya)\b"
)
_OTHER_PERSON_RE = re.compile(
    r"\b(mi|un|una) (amig[oa]|herman[oa]|prim[oa]|mama|papa|novi[oa]|companer[oa]|hij[oa]|familiar|conocid[oa])\b.{0,40}"
    r"\b(quiere|piensa|dijo|esta pensando|habla de|anda con)\b"
)


@dataclass
class SupportResult:
    kind: str                 # crisis | exercise | emotion
    intent: str               # crisis_support | wellbeing_exercise | emotional_support
    response: str
    sentiment: str            # positive | neutral | negative
    emotion: Optional[str] = None
    severity: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)


def _directly_negated(text: str, index: int) -> bool:
    """Negación pegada al término ("no me quiero morir", "no quiero matarme").

    Es estricta a propósito: una coma o una pausa corta la negación, porque en temas de
    seguridad es peor dejar pasar una crisis que mostrar apoyo de más.
    """
    return bool(re.search(r"\b(no|nunca|jamas|ni)\s+(\w+\s+)?$", text[:index]))


def _is_crisis(norm: str) -> bool:
    for rx in _CRISIS_RE:
        for m in rx.finditer(norm):
            if _directly_negated(norm, m.start()) and not re.match(r"no quiero|ya no quiero|no vale", m.group(0)):
                continue  # "no me quiero morir"
            return True
    return False


def _crisis_response(norm: str) -> SupportResult:
    other = bool(_OTHER_PERSON_RE.search(norm)) and not re.search(r"\b(yo|me)\b.{0,12}\b(quiero|voy)\b", norm)
    high = bool(_HIGH_RISK_RE.search(norm))

    if other:
        text = (
            "Gracias por contarme y por preocuparte por esa persona; eso ya es importante. "
            "Tomar en serio lo que dijo es lo correcto.\n\n"
            "• Habla con ella con calma y sin juzgar; pregúntale directamente cómo está. Preguntar no le da la idea.\n"
            "• No la dejes sola si sientes que está en peligro ahora.\n"
            f"• Pueden llamar a la {LINEA_106}. Si hay peligro inmediato, llama al {EMERGENCIAS}.\n\n"
            "¿Está contigo ahora o puedes comunicarte con ella?"
        )
        return SupportResult("crisis", "crisis_support", text, "negative", "crisis", "other",
                             ["Cómo hablarle", "Línea 106", "Estoy bien, gracias"])

    opening = (
        "Siento mucho que estés pasando por algo tan doloroso. Gracias por decírmelo; no tienes que cargarlo solo/a. "
        "Lo que sientes importa y tu vida importa."
    )
    if high:
        body = (
            f"\n\nPor lo que cuentas, es importante que busques ayuda ahora mismo: llama al {EMERGENCIAS} (emergencias) "
            f"o ve al servicio de urgencias más cercano. Si hay algo a tu alcance con lo que podrías hacerte daño, "
            f"aléjalo y pide a alguien que se quede contigo."
            f"\n\nTambién puedes llamar a la {LINEA_106}."
        )
    else:
        body = (
            f"\n\nTe pido algo: habla ahora con una persona. Puede ser alguien de confianza (familia, un amigo) "
            f"o la {LINEA_106}: ahí te escucharán personas preparadas. "
            f"Si sientes que podrías hacerte daño pronto, llama al {EMERGENCIAS}."
        )
    text = (
        f"{opening}{body}\n\n"
        "Yo soy un asistente y no puedo reemplazar a una persona que te acompañe. Aquí sigo contigo mientras tanto. "
        "¿Hay alguien cerca de ti ahora, o puedes escribirle o llamarle a alguien en este momento?"
    )
    return SupportResult("crisis", "crisis_support", text, "negative", "crisis",
                         "high" if high else "ideation",
                         ["Llamar a la Línea 106", "Hablar con alguien de confianza", "Ejercicio de respiración"])


# ---------------------------------------------------------------------------
# 2. Ejercicios
# ---------------------------------------------------------------------------
_PHYSICAL_RE = re.compile(
    r"\b(dolor (en|de) (el )?pecho|me duele el pecho|no puedo respirar|me falta el aire|me desmayo|"
    r"infarto|palpitaciones fuertes|entumec)"
)
_PHYSICAL_NOTE = (
    "Antes de nada: si tienes síntomas físicos fuertes (dolor en el pecho, falta de aire real, desmayos), "
    f"busca atención médica o llama al {EMERGENCIAS}. No puedo evaluar síntomas físicos.\n\n"
)

BREATHING = (
    "Hagamos una respiración lenta, juntos. Siéntate cómodo/a y suelta los hombros.\n\n"
    "1. Inhala por la nariz contando 4.\n"
    "2. Sostén el aire contando 4.\n"
    "3. Exhala despacio por la boca contando 6.\n"
    "4. Repite 5 veces, sin forzar. Si te mareas, vuelve a respirar normal.\n\n"
    "Cuando termines, cuéntame cómo te sientes (de 0 a 10)."
)
GROUNDING = (
    "Te llevo al presente con la técnica 5-4-3-2-1. Ve despacio:\n\n"
    "• 5 cosas que puedes VER\n• 4 cosas que puedes TOCAR\n• 3 cosas que puedes OÍR\n"
    "• 2 cosas que puedes OLER\n• 1 cosa que puedes SABOREAR\n\n"
    "Si quieres, escríbeme lo que fuiste encontrando."
)
VENT = (
    "Aquí tienes espacio para soltarlo. Escribe lo que quieras, como salga, sin ordenarlo ni justificarlo. "
    "Yo te leo y no te voy a apurar. ¿Qué es lo que más te pesa ahora?"
)
SPLIT = (
    "Cuando todo parece demasiado, ayuda partirlo:\n\n"
    "1. Escribe lo pendiente en una frase.\n"
    "2. Defínele el primer paso de 10 minutos o menos.\n"
    "3. Haz solo ese paso. Lo demás puede esperar.\n\n"
    "Si quieres, dime «crear tarea: …» con ese primer paso y lo dejo registrado."
)
_EXERCISES: List[Tuple[re.Pattern, str, str, List[str]]] = [
    (re.compile(r"respiracion|(ayudame|quiero|necesito|puedes ayudarme).{0,15}(a )?(respirar|calmarme|relajarme)|"
                r"(ejercicio|tecnica|guia|guiame|guiada).{0,20}(respir|relaj|calm)"), "respiración", BREATHING,
     ["Ejercicio 5-4-3-2-1", "Quiero desahogarme"]),
    (re.compile(r"5[ -]4[ -]3[ -]2[ -]1|grounding|anclaje|tecnica de los sentidos"), "anclaje", GROUNDING,
     ["Respiración guiada", "Quiero desahogarme"]),
    (re.compile(r"desahog|descargarme|soltar lo que siento|necesito hablar de lo que siento|quiero desahogarme"),
     "desahogo", VENT, ["Respiración guiada", "Ejercicio 5-4-3-2-1"]),
    (re.compile(r"(dividir|partir|dividirlo|partirlo|paso a paso).{0,25}(tarea|pendiente|todo)|"
                r"dividir lo pendiente"), "dividir tareas", SPLIT, ["Respiración guiada"]),
]


def _exercise(norm: str) -> Optional[SupportResult]:
    for rx, name, text, suggestions in _EXERCISES:
        if rx.search(norm):
            return SupportResult("exercise", "wellbeing_exercise", text, "neutral", name, None, suggestions)
    return None


# ---------------------------------------------------------------------------
# 3. Emociones
# ---------------------------------------------------------------------------
# Raíces (token.startswith) y frases. Todo sin tildes.
EMOTIONS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "ansiedad": {
        "stems": ("ansios", "ansied", "nervios", "angusti", "panico", "preocup", "inquiet", "taquicardia"),
        "phrases": ("no paro de pensar", "mil pensamientos", "no puedo dejar de pensar", "me da miedo", "se me acelera"),
    },
    "tristeza": {
        "stems": ("trist", "deprim", "lloro", "llorar", "llorando", "desanim", "melancol", "vacio", "desesper", "desolad"),
        "phrases": ("sin ganas", "no tengo ganas", "ganas de llorar", "sin animo", "sin esperanza", "todo me da igual"),
    },
    "estrés": {
        "stems": ("estres", "agobi", "abruma", "sobrecarg", "presion", "saturad", "colaps", "desbordad"),
        "phrases": ("demasiado trabajo", "no me da el tiempo", "no alcanzo", "mucha carga", "todo a la vez",
                    "muchas cosas pendientes", "no doy abasto"),
    },
    "enojo": {
        "stems": ("enoj", "rabia", "furios", "molest", "frustr", "irrit", "harto", "harta", "fastidi", "bronca"),
        "phrases": ("me tiene cansado de", "ya no aguanto a"),
    },
    "soledad": {
        "stems": ("soledad", "aislad"),
        "phrases": ("me siento solo", "me siento sola", "estoy solo", "estoy sola", "nadie me entiende",
                    "no tengo con quien", "nadie me escucha"),
    },
    "agotamiento": {
        "stems": ("cansad", "agotad", "fatig", "exhaust", "quemad"),
        "phrases": ("sin energia", "no doy mas", "no tengo energia", "burnout"),
    },
    "miedo": {
        "stems": ("miedo", "asustad", "temor", "aterrad", "insegur"),
        "phrases": ("me da pavor", "tengo miedo"),
    },
    "autocrítica": {
        "stems": (),
        "phrases": ("soy un fracaso", "soy inutil", "no sirvo para nada", "me odio", "soy un desastre",
                    "soy una carga", "no soy suficiente", "no soy capaz", "todo lo hago mal", "soy tonto", "soy tonta"),
    },
    "alegría": {
        "stems": ("content", "feliz", "felic", "alegr", "emocionad", "genial", "fantastic", "increible", "motivad"),
        "phrases": ("me siento bien", "estoy bien", "todo bien", "salio bien", "me fue bien", "muy buen dia"),
    },
    "gratitud": {
        "stems": ("agradecid", "gracias", "agradezco"),
        "phrases": (),
    },
    "orgullo": {
        "stems": ("orgullos",),
        "phrases": ("lo logre", "lo consegui", "termine todo", "cumpli mi meta", "aprobe"),
    },
    "calma": {
        "stems": ("tranquil", "relajad", "sereno", "serena", "en paz"),
        "phrases": ("me siento calmado", "me siento calmada"),
    },
}
NEGATIVE_EMOTIONS = {"ansiedad", "tristeza", "estrés", "enojo", "soledad", "agotamiento", "miedo", "autocrítica"}
POSITIVE_EMOTIONS = {"alegría", "gratitud", "orgullo", "calma"}
MIN_SCORE = 1.0

TOPICS = {
    "estudio": ("examen", "parcial", "universidad", "tesis", "exposicion", "estudiar", "clase", "colegio", "tarea de", "quiz", "notas"),
    "trabajo": ("trabajo", "jefe", "oficina", "entrega", "reunion", "cliente", "empleo", "proyecto", "deadline", "turno"),
    "familia": ("mama", "papa", "familia", "hermano", "hermana", "hijo", "hija", "casa"),
    "relaciones": ("novio", "novia", "pareja", "ex ", "amigo", "amiga", "terminamos", "pelee con"),
    "dinero": ("plata", "dinero", "deuda", "cuentas", "arriendo", "sueldo", "gastos"),
    "sueño": ("dormir", "sueno", "insomnio", "desvel", "no pude dormir"),
}


def detect_topics(norm: str) -> List[str]:
    return [t for t, words in TOPICS.items() if any(re.search(rf"\b{re.escape(w.strip())}", norm) for w in words)]


def detect_emotions(text: str) -> Dict[str, float]:
    """Puntúa emociones. Maneja negación (“no estoy triste”) e intensidad (“muy”, “un poco”)."""
    scores: Dict[str, float] = {}
    for clause in re.split(r"[,.;!?\n]|\bpero\b|\baunque\b|\by sin embargo\b", normalize(text)):
        clause = clause.strip()
        if not clause:
            continue
        tokens = clause.split()
        for emotion, lex in EMOTIONS.items():
            for phrase in lex["phrases"]:
                idx = clause.find(phrase)
                if idx == -1:
                    continue
                if not _negated_before(clause, idx, 10):
                    scores[emotion] = scores.get(emotion, 0) + 1.5
                elif emotion in POSITIVE_EMOTIONS:        # "no me siento bien"
                    scores["tristeza"] = scores.get("tristeza", 0) + 1.0
            for i, tok in enumerate(tokens):
                if len(tok) < 3 or not any(tok.startswith(s) for s in lex["stems"]):
                    continue
                weight = 1.0
                for prev in tokens[max(0, i - 2):i]:
                    weight *= INTENSIFIERS.get(prev, 1.0) * DIMINISHERS.get(prev, 1.0)
                if any(prev in NEGATORS for prev in tokens[max(0, i - 3):i]):
                    if emotion in POSITIVE_EMOTIONS:      # "no me siento feliz"
                        scores["tristeza"] = scores.get("tristeza", 0) + 1.0 * weight
                    continue                              # "no estoy triste" → ignora
                scores[emotion] = scores.get(emotion, 0) + weight
    return scores


_TOPIC_NUDGE = {
    "estudio": "Si es por el estudio, podemos partir lo que falta en pasos pequeños y dejarlos como tareas.",
    "trabajo": "Si es por el trabajo, podemos ordenar lo pendiente y elegir solo lo que de verdad toca hoy.",
    "familia": "Las cosas de familia pesan distinto; no hace falta resolverlas hoy.",
    "relaciones": "Las relaciones nos mueven mucho por dentro; es normal que esto te afecte.",
    "dinero": "El tema de plata genera mucha presión; si quieres, lo vamos desglosando en pasos concretos.",
    "sueño": "Dormir mal intensifica todo lo demás; vale la pena cuidar el descanso de esta noche.",
}

_RESPONSES: Dict[str, List[str]] = {
    "ansiedad": [
        "Se nota que hay mucha inquietud en este momento, y es una sensación muy incómoda. No estás haciendo nada mal por sentirla.",
        "Gracias por contármelo. La ansiedad hace que todo se sienta urgente aunque no lo sea; vayamos por partes.",
    ],
    "tristeza": [
        "Lamento que te sientas así. Está bien no estar bien; no tienes que fingir ni solucionarlo todo hoy.",
        "Gracias por confiarme esto. Lo que sientes es real y merece espacio. Aquí estoy para escucharte.",
    ],
    "estrés": [
        "Suena a que estás cargando demasiado a la vez. Eso agota a cualquiera, y no es un problema de tu capacidad.",
        "Entiendo la presión. Cuando todo llega junto, el cerebro lo vive como una sola montaña; podemos separarla.",
    ],
    "enojo": [
        "Tiene sentido que estés molesto/a; la frustración suele avisar que algo importante no se está respetando.",
        "Gracias por decirlo sin guardártelo. Soltar el enojo con calma ayuda a pensar mejor después.",
    ],
    "soledad": [
        "Sentirse solo/a duele, y que lo digas ya es un paso valioso. Aquí puedes hablar con calma.",
        "Gracias por abrirte. La soledad pesa mucho; no tienes que atravesarla sin compañía.",
    ],
    "agotamiento": [
        "Parece que estás muy agotado/a. Descansar no es un lujo; es parte de poder seguir.",
        "El cansancio acumulado te está pasando factura. Reducir un poco la carga hoy puede ser lo más productivo.",
    ],
    "miedo": [
        "El miedo se siente muy fuerte cuando se mira todo de golpe. Vamos a mirar solo lo más cercano.",
        "Gracias por decirlo. Sentir miedo es humano; no significa que no puedas con esto.",
    ],
    "autocrítica": [
        "Te hablas con mucha dureza, y esa voz no es un juicio justo sobre quien eres. No le debes perfección a nadie.",
        "Lamento que te estés tratando así. Un mal momento o un error no define tu valor.",
    ],
    "alegría": [
        "¡Qué bueno leerte así! Disfruta este momento.",
        "Me alegra mucho. Vale la pena notar qué te ayudó a llegar aquí.",
    ],
    "gratitud": ["Con gusto. Me alegra poder acompañarte."],
    "orgullo": [
        "¡Felicitaciones! Ese logro es fruto de tu esfuerzo. Tómate un momento para reconocerlo.",
        "¡Excelente! Lo lograste y eso cuenta. Celébralo a tu manera.",
    ],
    "calma": [
        "Qué bien que te sientas en calma. Es un buen momento para aprovechar esa claridad.",
    ],
}

_FOLLOW_UP = {
    "ansiedad": "¿Quieres que probemos una respiración guiada o prefieres contarme qué pasa?",
    "tristeza": "¿Quieres contarme qué pasó o prefieres un ejercicio corto para soltar tensión?",
    "estrés": "¿Te ayudo a dividir lo pendiente en pasos pequeños, o prefieres primero una pausa de respiración?",
    "enojo": "¿Quieres desahogarte aquí o prefieres una respiración para bajar la tensión?",
    "soledad": "¿Hay alguien con quien te gustaría reconectar? Podemos pensar un mensaje sencillo para escribirle.",
    "agotamiento": "¿Quieres que revisemos tus tareas de hoy y dejemos solo lo esencial?",
    "miedo": "¿Qué es lo que más te preocupa? Podemos mirarlo juntos paso a paso.",
    "autocrítica": "¿Qué le dirías a un buen amigo en tu misma situación? Cuéntame qué pasó y lo miramos con más justicia.",
    "alegría": "¿Quieres convertir esto en un hábito que ayude a sostener cómo te sientes?",
    "orgullo": "¿Qué te gustaría lograr a continuación? Puedo ayudarte a planificarlo.",
    "calma": "¿Quieres usar este ánimo para avanzar con alguna tarea pendiente?",
    "gratitud": "¿Hay algo más en lo que pueda ayudarte hoy?",
}
_SUGGESTIONS = {
    "negative": ["Respiración guiada", "Ejercicio 5-4-3-2-1", "Quiero desahogarme", "Dividir lo pendiente en tareas"],
    "positive": ["Crear un hábito", "Ver mis tareas"],
}
_PROFESSIONAL_NOTE = (
    "\n\nSi esto se siente muy pesado o lleva mucho tiempo, hablarlo con una persona de confianza o con un "
    f"profesional puede ayudar mucho. La {LINEA_106} está disponible si lo necesitas."
)

# Mensajes que son órdenes explícitas deben llegar al clasificador de intenciones
_COMMAND_RE = re.compile(
    r"\b(crear?|crea|agrega(r)?|anadi(r)?|nueva|nuevo|registra(r)?|recuerdame|programa(r)?)\b.{0,40}\b(tarea|habito|recordatorio|evento)\b|"
    r"\b(mis|lista de|mostrar|muestrame|ver|ensename)\b.{0,15}\b(tareas|habitos)\b|^(crear|nueva tarea|nuevo habito)"
)


def is_explicit_command(norm: str) -> bool:
    return bool(_COMMAND_RE.search(norm))


def _emotion_response(emotion: str, score: float, norm: str, rng: random.Random) -> SupportResult:
    topics = detect_topics(norm)
    parts = [rng.choice(_RESPONSES[emotion])]
    if emotion in NEGATIVE_EMOTIONS and topics:
        parts.append(_TOPIC_NUDGE[topics[0]])
    parts.append(_FOLLOW_UP[emotion])
    text = " ".join(parts[:2]) + "\n\n" + parts[2] if len(parts) == 3 else " ".join(parts)
    if _PHYSICAL_RE.search(norm):
        text = _PHYSICAL_NOTE + text
    if emotion in NEGATIVE_EMOTIONS and score >= 3.0:
        text += _PROFESSIONAL_NOTE
    sentiment = "negative" if emotion in NEGATIVE_EMOTIONS else "positive"
    return SupportResult("emotion", "emotional_support", text, sentiment, emotion, None,
                         _SUGGESTIONS[sentiment], topics)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def check_crisis(message: str) -> Optional[SupportResult]:
    """Detecta crisis. Debe llamarse SIEMPRE primero, antes de cualquier otro flujo."""
    norm = normalize(message)
    return _crisis_response(norm) if _is_crisis(norm) else None


def analyze(message: str, rng: Optional[random.Random] = None) -> Optional[SupportResult]:
    """Ejercicio o emoción detectada con confianza; None si el mensaje debe seguir el flujo normal."""
    norm = normalize(message)
    if not norm or is_explicit_command(norm):
        return None
    if _PHYSICAL_RE.search(norm) and not _exercise(norm):
        scores = detect_emotions(message)
        if not scores:
            return SupportResult("emotion", "emotional_support", _PHYSICAL_NOTE.strip(), "negative", "ansiedad",
                                 None, _SUGGESTIONS["negative"])
    exercise = _exercise(norm)
    if exercise:
        return exercise
    scores = detect_emotions(message)
    if not scores:
        return None
    emotion, score = max(scores.items(), key=lambda kv: kv[1])
    if score < MIN_SCORE:
        return None
    return _emotion_response(emotion, score, norm, rng or random.Random())


_FIRST_PERSON_RE = re.compile(r"\b(me siento|me estoy sintiendo|estoy|siento|tengo|me da|me tiene|me pone|soy|no puedo|me duele|me\b)")


def is_first_person(message: str) -> bool:
    """¿La persona habla de cómo está ella? Distingue «estoy estresado» de «meditar para el estrés»."""
    return bool(_FIRST_PERSON_RE.search(normalize(message)))


def to_response(result: SupportResult) -> Dict[str, object]:
    """Formato de respuesta que consume la API del chat."""
    from datetime import datetime
    is_crisis = result.kind == "crisis"
    return {
        "response": result.response,
        "intent": result.intent,
        "confidence": 1.0,
        "sentiment": result.sentiment,
        "sentiment_confidence": 1.0 if is_crisis else 0.8,
        "suggestions": result.suggestions,
        "entities": {"topics": result.topics} if result.topics else {},
        "emotion": None if is_crisis else result.emotion,  # no se persiste nada de las crisis
        "crisis": is_crisis,
        "timestamp": datetime.utcnow().isoformat(),
    }
