"""Cálculo de analíticas (puro, sin FastAPI) a partir de tareas, hábitos y mensajes del chat.

Todas las fechas de la base de datos son UTC "naive". El parámetro ``tz_offset`` son
los minutos al este de UTC del dispositivo (p. ej. Colombia = -300) y solo se usa para
mostrar horas y días pico en hora local.
"""
from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timedelta, date
from typing import Any, Dict, Iterable, List, Optional

PERIOD_DAYS = {"week": 7, "month": 30, "year": 365}
DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
PRIORITY_VALUE = {"low": 1, "medium": 2, "high": 3}
INTENT_LABELS = {
    "greeting": "Saludo",
    "create_task": "Crear tareas",
    "create_habit": "Crear hábitos",
    "list_tasks": "Consultar tareas",
    "list_habits": "Consultar hábitos",
    "productivity_tips": "Consejos de productividad",
    "motivation": "Motivación",
    "emotional_support": "Apoyo emocional",
    "wellbeing_exercise": "Ejercicios de bienestar",
    "crisis_support": "Apoyo en crisis",
    "help": "Ayuda",
    "goodbye": "Despedida",
    "unknown": "Otros",
}
SENTIMENT_VALUE = {"positive": 1, "neutral": 0, "negative": -1}
SESSION_GAP = timedelta(minutes=30)


def normalize_period(period: Optional[str]) -> str:
    return period if period in PERIOD_DAYS else "week"


def _pct(part: float, whole: float) -> float:
    return round(part / whole * 100, 1) if whole else 0.0


def _trend(current: float, previous: float) -> Optional[int]:
    """Cambio porcentual frente al periodo anterior; None si no hay con qué comparar."""
    if not previous:
        return None
    return int(round((current - previous) / previous * 100))


def _in(dt: Optional[datetime], start: datetime, end: datetime) -> bool:
    # (inicio, fin]: el instante actual cuenta y los periodos consecutivos no se solapan
    return dt is not None and start < dt <= end


def _local(dt: datetime, tz_offset: int) -> datetime:
    return dt + timedelta(minutes=tz_offset)


def _longest_run(days: Iterable[date]) -> int:
    ordered = sorted(set(days))
    best = run = 0
    prev = None
    for d in ordered:
        run = run + 1 if prev is not None and d - prev == timedelta(days=1) else 1
        best = max(best, run)
        prev = d
    return best


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------
def task_stats(tasks: List[Any], start: datetime, end: datetime) -> Dict[str, Any]:
    scope = [t for t in tasks if _in(t.created_at, start, end) or _in(t.completed_at, start, end)]
    completed = [t for t in tasks if _in(t.completed_at, start, end)]
    return {
        "scope": scope,
        "total": len(scope),
        "completed": len(completed),
        "completed_list": completed,
        "rate": min(_pct(len(completed), len(scope)), 100.0),
    }


def _avg_priority_label(tasks: List[Any]) -> Optional[str]:
    values = [PRIORITY_VALUE[t.priority] for t in tasks if t.priority in PRIORITY_VALUE]
    if not values:
        return None
    mean = sum(values) / len(values)
    return "Baja" if mean < 1.67 else "Media" if mean < 2.34 else "Alta"


def _format_minutes(minutes: float) -> str:
    minutes = int(round(minutes))
    if minutes < 60:
        return f"{minutes} min"
    h, m = divmod(minutes, 60)
    return f"{h} h" if m == 0 else f"{h} h {m} min"


# ---------------------------------------------------------------------------
# Hábitos
# ---------------------------------------------------------------------------
def habit_stats(habits: List[Any], logs_by_habit: Dict[int, List[datetime]],
                start: datetime, end: datetime) -> Dict[str, Any]:
    """Constancia: cumplimientos reales / cumplimientos esperados en el periodo.

    Esperados: diarios = días de vida del hábito dentro del periodo; semanales/mensuales
    = semanas/meses de vida (mínimo 1). La vida arranca en la fecha de creación o en el
    primer registro, lo que ocurra antes (así los registros retroactivos no inflan nada).
    """
    expected_total = done_total = completions = 0
    per_habit: List[Dict[str, Any]] = []
    longest = 0
    window_days = max((end - start).days, 1)

    for habit in habits:
        if not habit.is_active:
            continue
        window_logs = [d for d in logs_by_habit.get(habit.id, []) if _in(d, start, end)]
        completions += len(window_logs)
        first = min([habit.created_at] + window_logs) if habit.created_at else (min(window_logs) if window_logs else None)
        if first is None:
            continue
        life_start = max(first, start)
        life_days = max(1, min(window_days, (end.date() - life_start.date()).days + 1))

        if habit.frequency == "weekly":
            expected = max(1, math.ceil(life_days / 7))
            done = len({(d.isocalendar()[0], d.isocalendar()[1]) for d in window_logs})
        elif habit.frequency == "monthly":
            expected = max(1, math.ceil(life_days / 30))
            done = len({(d.year, d.month) for d in window_logs})
        else:
            expected = life_days
            done = len({d.date() for d in window_logs})
        done = min(done, expected)

        expected_total += expected
        done_total += done
        longest = max(longest, _longest_run(d.date() for d in window_logs))
        per_habit.append({"name": habit.name, "count": len(window_logs), "done": done, "expected": expected})

    best = max(per_habit, key=lambda h: (h["count"], h["done"]), default=None)
    return {
        "adherence": _pct(done_total, expected_total) if expected_total else None,
        "completions": completions,
        "longest_streak": longest,
        "most_successful": best["name"] if best and best["count"] > 0 else None,
    }


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
def chat_stats(messages: List[Any], start: datetime, end: datetime) -> Dict[str, Any]:
    window = sorted((m for m in messages if _in(m.created_at, start, end)), key=lambda m: m.created_at)
    sessions = 0
    last = None
    for m in window:
        if last is None or m.created_at - last > SESSION_GAP:
            sessions += 1
        last = m.created_at
    intents = Counter(m.intent for m in window if m.intent)
    sentiments = [SENTIMENT_VALUE[m.sentiment] for m in window if m.sentiment in SENTIMENT_VALUE]
    mean = sum(sentiments) / len(sentiments) if sentiments else None
    return {
        "messages": len(window),
        "sessions": sessions,
        "top_intent": intents.most_common(1)[0][0] if intents else None,
        "sentiment_mean": mean,
        "negative_share": (sum(1 for s in sentiments if s < 0) / len(sentiments)) if sentiments else 0.0,
    }


def _sentiment_label(mean: Optional[float]) -> Optional[str]:
    if mean is None:
        return None
    return "Positivo" if mean > 0.2 else "Negativo" if mean < -0.2 else "Neutral"


# ---------------------------------------------------------------------------
# Puntaje global
# ---------------------------------------------------------------------------
def _score(task_rate: Optional[float], adherence: Optional[float]) -> int:
    if task_rate is not None and adherence is not None:
        return int(round(0.6 * task_rate + 0.4 * adherence))
    if task_rate is not None:
        return int(round(task_rate))
    if adherence is not None:
        return int(round(adherence))
    return 0


def compute_analytics(tasks: List[Any], habits: List[Any], habit_logs: List[Any],
                      chat_messages: List[Any], period: str = "week", tz_offset: int = 0,
                      now: Optional[datetime] = None) -> Dict[str, Any]:
    """Devuelve todas las secciones que consume la pantalla de Analytics."""
    period = normalize_period(period)
    now = now or datetime.utcnow()
    days = PERIOD_DAYS[period]
    start, end = now - timedelta(days=days), now
    prev_start, prev_end = start - timedelta(days=days), start

    logs_by_habit: Dict[int, List[datetime]] = {}
    for log in habit_logs:
        if log.completed_at:
            logs_by_habit.setdefault(log.habit_id, []).append(log.completed_at)

    cur_t, prev_t = task_stats(tasks, start, end), task_stats(tasks, prev_start, prev_end)
    cur_h = habit_stats(habits, logs_by_habit, start, end)
    prev_h = habit_stats(habits, logs_by_habit, prev_start, prev_end)
    cur_c, prev_c = chat_stats(chat_messages, start, end), chat_stats(chat_messages, prev_start, prev_end)

    task_rate = cur_t["rate"] if cur_t["total"] else None
    prev_task_rate = prev_t["rate"] if prev_t["total"] else None
    score = _score(task_rate, cur_h["adherence"])
    prev_score = _score(prev_task_rate, prev_h["adherence"])

    # Momentos en que la persona suele cumplir cosas (tareas + hábitos), en hora local
    moments = [_local(t.completed_at, tz_offset) for t in cur_t["completed_list"]]
    for habit in habits:
        moments += [_local(d, tz_offset) for d in logs_by_habit.get(habit.id, []) if _in(d, start, end)]
    peak_hour = Counter(m.hour for m in moments).most_common(1)
    peak_day = Counter(m.weekday() for m in moments).most_common(1)

    estimates = [t.estimated_time for t in cur_t["scope"] if t.estimated_time]
    categories = Counter(t.category for t in cur_t["scope"] if t.category)

    active_habits = [h for h in habits if h.is_active]
    summary = {
        "productivity_score": score,
        "productivity_trend": _trend(score, prev_score) if prev_score else None,
        "tasks_completed": cur_t["completed"],
        "total_tasks": cur_t["total"],
        "tasks_trend": _trend(cur_t["completed"], prev_t["completed"]),
        "habits_active": len(active_habits),
        "total_habits": len(habits),
        "habits_trend": _trend(cur_h["completions"], prev_h["completions"]),
        "chat_sessions": cur_c["sessions"],
        "chat_trend": _trend(cur_c["sessions"], prev_c["sessions"]),
    }
    productivity = {
        "peak_hours": f"{peak_hour[0][0]:02d}:00 - {(peak_hour[0][0] + 1) % 24:02d}:00" if peak_hour else None,
        "peak_day": DAY_NAMES[peak_day[0][0]] if peak_day else None,
        "avg_task_time": _format_minutes(sum(estimates) / len(estimates)) if estimates else None,
    }
    tasks_section = {
        "completion_rate": cur_t["rate"],
        "top_category": categories.most_common(1)[0][0] if categories else None,
        "avg_priority": _avg_priority_label(cur_t["scope"]),
    }
    habits_section = {
        "adherence_rate": cur_h["adherence"] if cur_h["adherence"] is not None else 0,
        "longest_streak": cur_h["longest_streak"],
        "most_successful": cur_h["most_successful"],
    }
    chat_section = {
        "messages_sent": cur_c["messages"],
        "top_intent": INTENT_LABELS.get(cur_c["top_intent"], cur_c["top_intent"]) if cur_c["top_intent"] else None,
        "avg_sentiment": _sentiment_label(cur_c["sentiment_mean"]),
    }

    overdue = [t for t in tasks if t.status in ("pending", "in_progress") and t.due_date and t.due_date < now]
    insights = build_insights(
        summary=summary, productivity=productivity, habits=habits_section, chat=chat_section,
        overdue=len(overdue), negative_share=cur_c["negative_share"], chat_messages=cur_c["messages"],
        has_data=bool(tasks or habits),
    )
    return {
        "period": period,
        "summary": summary,
        "productivity": productivity,
        "tasks": tasks_section,
        "habits": habits_section,
        "chat": chat_section,
        "insights": insights,
    }


def build_insights(*, summary, productivity, habits, chat, overdue, negative_share, chat_messages, has_data) -> List[str]:
    """Recomendaciones basadas en reglas, en español. Son observaciones, no diagnósticos."""
    if not has_data:
        return ["Aún no hay suficientes datos. Crea algunas tareas o hábitos y marca tu progreso para ver recomendaciones aquí."]

    out: List[str] = []
    trend = summary.get("tasks_trend")
    done = summary.get("tasks_completed", 0)
    if done and trend is not None:
        if trend > 0:
            out.append(f"Completaste {done} tareas, {trend}% más que en el periodo anterior. ¡Buen ritmo!")
        elif trend < 0:
            out.append(f"Completaste {done} tareas, {abs(trend)}% menos que antes. Si hubo una semana pesada, está bien: elige una sola tarea pequeña para retomar.")
    if overdue:
        plural = "s" if overdue > 1 else ""
        out.append(f"Tienes {overdue} tarea{plural} vencida{plural}. Empieza por la más pequeña: avanzar un poco ya cambia el panorama.")

    adherence = habits.get("adherence_rate") or 0
    if summary.get("habits_active"):
        if adherence >= 80:
            out.append(f"Tu constancia en hábitos es de {adherence:g}%. Mantén lo que estás haciendo.")
        elif adherence < 50:
            out.append(f"Tu constancia en hábitos es de {adherence:g}%. Prueba con un solo hábito y hazlo tan pequeño que sea difícil fallar.")
    if habits.get("longest_streak", 0) >= 3 and habits.get("most_successful"):
        out.append(f"Llevas hasta {habits['longest_streak']} días seguidos de constancia; «{habits['most_successful']}» es tu hábito más sólido.")

    if productivity.get("peak_hours"):
        out.append(f"Sueles cumplir más cosas entre {productivity['peak_hours']}. Reserva ese bloque para lo que más te cuesta.")

    if chat_messages >= 3 and negative_share >= 0.5:
        msg = "En tus conversaciones recientes se nota cansancio o tensión. Considera bajar la carga de hoy y hacer una pausa."
        if trend is not None and trend < 0:
            msg += " Este periodo coincidió un ánimo más bajo con menos tareas completadas; no es una falla tuya, ajusta la carga."
        out.append(msg)

    return out[:5] or ["Vas bien. Sigue registrando tus tareas y hábitos para obtener recomendaciones más precisas."]
