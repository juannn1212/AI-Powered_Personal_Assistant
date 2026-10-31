from datetime import datetime, timedelta
from types import SimpleNamespace as NS

from app.services.analytics_service import compute_analytics

NOW = datetime(2026, 10, 28, 15, 0, 0)  # miércoles


def task(i, created_days_ago, completed_days_ago=None, **kw):
    return NS(id=i, created_at=NOW - timedelta(days=created_days_ago),
              completed_at=(NOW - timedelta(days=completed_days_ago)) if completed_days_ago is not None else None,
              status="completed" if completed_days_ago is not None else kw.pop("status", "pending"),
              priority=kw.get("priority", "medium"), category=kw.get("category"),
              due_date=kw.get("due_date"), estimated_time=kw.get("estimated_time"))


def habit(i, days_old=10, frequency="daily", name="Caminar", active=True):
    return NS(id=i, name=name, frequency=frequency, is_active=active, created_at=NOW - timedelta(days=days_old))


def log(habit_id, days_ago, hour=8):
    return NS(habit_id=habit_id, completed_at=(NOW - timedelta(days=days_ago)).replace(hour=hour))


def run(tasks=(), habits=(), logs=(), chat=(), **kw):
    return compute_analytics(list(tasks), list(habits), list(logs), list(chat), now=NOW, **kw)


def test_sin_datos_todo_en_cero_y_sin_tendencias():
    r = run()
    assert r["summary"]["productivity_score"] == 0
    assert r["summary"]["tasks_trend"] is None
    assert r["productivity"]["peak_hours"] is None
    assert "Aún no hay suficientes datos" in r["insights"][0]


def test_tareas_completadas_y_tasa():
    tasks = [task(1, 2, 1), task(2, 3, 0), task(3, 1), task(4, 2)]
    r = run(tasks)
    assert r["summary"]["tasks_completed"] == 2 and r["summary"]["total_tasks"] == 4
    assert r["tasks"]["completion_rate"] == 50.0


def test_el_periodo_cambia_el_alcance():
    tasks = [task(1, 20, 15), task(2, 2, 1)]
    assert run(tasks, period="week")["summary"]["total_tasks"] == 1
    assert run(tasks, period="month")["summary"]["total_tasks"] == 2
    assert run(tasks, period="valor-invalido")["period"] == "week"


def test_tendencia_frente_al_periodo_anterior():
    tasks = [task(1, 2, 1), task(2, 2, 1), task(3, 2, 1), task(4, 9, 8), task(5, 9, 9)]
    assert run(tasks)["summary"]["tasks_trend"] == 50  # 3 vs 2


def test_adherencia_diaria_no_se_infla_con_registros_retroactivos():
    h = habit(1, days_old=2)
    logs = [log(1, d) for d in range(0, 7)]  # 7 días registrados aunque el hábito "nació" hace 2
    r = run(habits=[h], logs=logs)
    assert r["habits"]["adherence_rate"] == 100.0
    assert r["habits"]["longest_streak"] == 7
    assert r["habits"]["most_successful"] == "Caminar"


def test_adherencia_parcial():
    h = habit(1, days_old=20)
    r = run(habits=[h], logs=[log(1, 0), log(1, 1), log(1, 2), log(1, 3)])
    assert r["habits"]["adherence_rate"] == round(4 / 7 * 100, 1)


def test_habito_semanal():
    h = habit(1, days_old=20, frequency="weekly")
    r = run(habits=[h], logs=[log(1, 0)])
    assert r["habits"]["adherence_rate"] == 100.0


def test_habitos_inactivos_no_cuentan():
    r = run(habits=[habit(1, active=False)], logs=[log(1, 0)])
    assert r["summary"]["habits_active"] == 0 and r["habits"]["adherence_rate"] == 0


def test_hora_pico_respeta_zona_horaria():
    tasks = [task(1, 2, 1)]  # completada a las 15:00 UTC
    assert run(tasks)["productivity"]["peak_hours"] == "15:00 - 16:00"
    assert run(tasks, tz_offset=-300)["productivity"]["peak_hours"] == "10:00 - 11:00"


def test_dia_pico_en_espanol():
    r = run([task(1, 2, 1)])  # completada el martes 27
    assert r["productivity"]["peak_day"] == "Martes"


def test_chat_sesiones_intencion_y_sentimiento():
    chat = [NS(created_at=NOW - timedelta(hours=h), intent="emotional_support", emotion="ansiedad", sentiment="negative")
            for h in (1.0, 0.9, 0.8)]
    chat.append(NS(created_at=NOW - timedelta(hours=10), intent="create_task", emotion=None, sentiment="neutral"))
    r = run(chat=chat)
    assert r["chat"]["messages_sent"] == 4
    assert r["summary"]["chat_sessions"] == 2
    assert r["chat"]["top_intent"] == "Apoyo emocional"
    assert r["chat"]["avg_sentiment"] == "Negativo"


def test_insights_tareas_vencidas_y_animo():
    overdue = task(1, 5, status="pending", due_date=NOW - timedelta(days=1))
    chat = [NS(created_at=NOW - timedelta(hours=h), intent="emotional_support", emotion="estrés", sentiment="negative")
            for h in (3, 2, 1)]
    r = run([overdue], chat=chat)
    joined = " ".join(r["insights"])
    assert "vencida" in joined and "cansancio o tensión" in joined
    assert len(r["insights"]) <= 5
