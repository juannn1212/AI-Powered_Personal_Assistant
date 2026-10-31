import random

import pytest

from app.services.emotional_support import analyze, check_crisis, detect_emotions, is_explicit_command, normalize


# ---- Crisis -----------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "me quiero morir",
    "Ya no quiero vivir así",
    "a veces pienso en quitarme la vida",
    "no sé, quiero morirme",
    "estoy pensando en suicidarme",
    "me voy a matar",
    "quiero hacerme daño",
    "ME QUIERO MORIR!!!",
])
def test_detecta_crisis(text):
    result = check_crisis(text)
    assert result is not None and result.kind == "crisis"


@pytest.mark.parametrize("text", [
    "no me quiero morir",
    "no quiero morir",
    "hola, ¿cómo estás?",
    "estoy muerto de sueño",
    "crear tarea: entregar el informe",
    "me mata el estrés de esta semana",
])
def test_no_confunde_frases_normales_con_crisis(text):
    assert check_crisis(text) is None


def test_crisis_incluye_recursos_y_no_valida_el_deseo():
    text = check_crisis("me quiero morir").response
    assert "106" in text and "123" in text
    for banned in ("tiene sentido que quieras", "es razonable", "tu decisión", "respeto tu decisión"):
        assert banned not in text.lower()


def test_riesgo_alto_prioriza_emergencias():
    result = check_crisis("tengo un plan para matarme esta noche")
    assert result.severity == "high"
    assert result.response.index("123") < result.response.index("106")


def test_crisis_sobre_otra_persona():
    result = check_crisis("mi amigo quiere suicidarse")
    assert result.severity == "other"
    assert "106" in result.response


# ---- Emociones ----------------------------------------------------------------
@pytest.mark.parametrize("text,emotion", [
    ("Me siento ansioso por la presentación de mañana", "ansiedad"),
    ("estoy muy triste hoy", "tristeza"),
    ("me siento agobiado con tantos parciales", "estrés"),
    ("estoy furioso con mi jefe", "enojo"),
    ("me siento sola", "soledad"),
    ("estoy agotado, no tengo energía", "agotamiento"),
    ("soy un fracaso, me odio", "autocrítica"),
    ("lo logré, estoy muy orgulloso", "orgullo"),
    ("estoy muy feliz", "alegría"),
])
def test_detecta_emocion_principal(text, emotion):
    result = analyze(text, random.Random(0))
    assert result is not None and result.emotion == emotion


def test_negacion_no_activa_emocion_negativa():
    assert detect_emotions("no estoy triste") .get("tristeza", 0) == 0
    assert analyze("no me siento ansioso") is None


def test_negacion_de_positivo_cuenta_como_malestar():
    result = analyze("no me siento bien")
    assert result is not None and result.emotion == "tristeza"


def test_intensidad_modifica_puntaje():
    fuerte = detect_emotions("estoy muy muy triste")["tristeza"]
    suave = detect_emotions("estoy un poco triste")["tristeza"]
    assert fuerte > suave


def test_mensajes_neutros_siguen_el_flujo_normal():
    assert analyze("hola") is None
    assert analyze("¿qué tengo pendiente para hoy?") is None


def test_ordenes_explicitas_no_se_interceptan():
    assert analyze("crear tarea: hablar con mi jefe porque estoy estresado") is None
    assert analyze("muéstrame mis tareas") is None
    assert is_explicit_command(normalize("agregar hábito de meditar"))


def test_respuesta_negativa_ofrece_ejercicios_y_tema():
    result = analyze("me siento muy estresado por los parciales", random.Random(1))
    assert result.sentiment == "negative"
    assert "estudio" in result.topics
    assert any("espiración" in s for s in result.suggestions)


def test_sintomas_fisicos_incluyen_nota_de_atencion_medica():
    result = analyze("me duele el pecho y estoy muy ansioso", random.Random(0))
    assert "123" in result.response


# ---- Ejercicios ------------------------------------------------------------------
@pytest.mark.parametrize("text,name", [
    ("dame un ejercicio de respiración", "respiración"),
    ("quiero hacer la técnica 5-4-3-2-1", "anclaje"),
    ("necesito desahogarme", "desahogo"),
])
def test_ejercicios(text, name):
    result = analyze(text)
    assert result.kind == "exercise" and result.emotion == name


def test_toda_emocion_del_lexico_tiene_respuesta_y_seguimiento():
    """Evita KeyError en producción si se agrega una emoción al léxico sin su respuesta."""
    from app.services import emotional_support as es
    for emotion in es.EMOTIONS:
        assert emotion in es._RESPONSES, emotion
        assert emotion in es._FOLLOW_UP, emotion
        result = es._emotion_response(emotion, 1.0, "texto", random.Random(0))
        assert result.response and result.sentiment in ("negative", "positive")


def test_gracias_no_rompe():
    assert analyze("ya me siento un poco mejor, gracias").emotion == "gratitud"
