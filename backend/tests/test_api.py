from datetime import datetime, timedelta


def _task(client, h, **kw):
    body = {"title": "Tarea", "priority": "medium", "status": "pending", **kw}
    r = client.post("/api/tasks/", json=body, headers=h)
    assert r.status_code == 200, r.text
    return r.json()


# ---- Tareas / hábitos --------------------------------------------------------
def test_stats_de_tareas_usa_los_nombres_que_espera_el_frontend(client, auth):
    h, _ = auth
    t = _task(client, h, title="A")
    _task(client, h, title="B")
    assert client.post(f"/api/tasks/{t['id']}/complete", headers=h).status_code == 200
    stats = client.get("/api/tasks/stats/summary", headers=h).json()
    assert (stats["total"], stats["completed"], stats["pending"]) == (2, 1, 1)
    assert stats["total_tasks"] == 2


def test_habito_toggle_y_racha(client, auth):
    h, _ = auth
    hab = client.post("/api/habits/", json={"name": "Leer"}, headers=h).json()
    assert hab["completed_today"] is False and hab["streak"] == 0
    on = client.post(f"/api/habits/{hab['id']}/toggle", headers=h).json()
    assert on["completed_today"] is True and on["streak"] == 1
    off = client.post(f"/api/habits/{hab['id']}/toggle", headers=h).json()
    assert off["completed_today"] is False
    ayer = (datetime.utcnow() - timedelta(days=1)).isoformat()
    client.post(f"/api/habits/{hab['id']}/log", json={"completed_at": ayer}, headers=h)
    client.post(f"/api/habits/{hab['id']}/toggle", headers=h)
    stats = client.get("/api/habits/stats/summary", headers=h).json()
    assert stats["max_streak"] == 2 and stats["completed_today"] == 1


def test_datos_aislados_entre_usuarios(client, auth):
    h, _ = auth
    _task(client, h, title="Privada")
    other = client.post("/api/auth/register", json={"email": "otro@test.com", "password": "Test-pass-123", "full_name": "Otro"})
    h2 = {"Authorization": f"Bearer {other.json()['access_token']}"}
    assert client.get("/api/tasks/", headers=h2).json() == []


# ---- Analytics ------------------------------------------------------------------
def test_analytics_devuelve_la_forma_que_consume_la_pantalla(client, auth):
    h, _ = auth
    t = _task(client, h, title="X", category="Trabajo", estimated_time=30)
    client.post(f"/api/tasks/{t['id']}/complete", headers=h)
    hab = client.post("/api/habits/", json={"name": "Meditar"}, headers=h).json()
    client.post(f"/api/habits/{hab['id']}/toggle", headers=h)

    summary = client.get("/api/analytics/summary?period=week&tz_offset=-300", headers=h).json()
    for key in ("productivity_score", "productivity_trend", "tasks_completed", "total_tasks", "tasks_trend",
                "habits_active", "total_habits", "habits_trend", "chat_sessions", "chat_trend"):
        assert key in summary
    assert summary["tasks_completed"] == 1 and summary["habits_active"] == 1
    assert summary["productivity_score"] == 100

    assert client.get("/api/analytics/tasks", headers=h).json()["top_category"] == "Trabajo"
    assert client.get("/api/analytics/habits?period=month", headers=h).json()["most_successful"] == "Meditar"
    prod = client.get("/api/analytics/productivity", headers=h).json()
    assert set(prod) == {"peak_hours", "peak_day", "avg_task_time"} and prod["avg_task_time"] == "30 min"
    insights = client.get("/api/analytics/insights", headers=h)
    assert insights.status_code == 200 and isinstance(insights.json()["insights"], list)


def test_analytics_periodo_invalido_no_rompe(client, auth):
    h, _ = auth
    assert client.get("/api/analytics/summary?period=siglo", headers=h).status_code == 200


def test_analytics_requiere_autenticacion(client):
    assert client.get("/api/analytics/summary").status_code in (401, 403)


# ---- Chat ----------------------------------------------------------------------
def _chat(client, h, text):
    r = client.post("/api/assistant/chat", json={"message": text}, headers=h)
    assert r.status_code == 200, r.text
    return r.json()["data"]


def test_chat_crisis_responde_con_recursos(client, auth):
    h, _ = auth
    data = _chat(client, h, "me quiero morir")
    assert data["intent"] == "crisis_support" and data["crisis"] is True
    assert "106" in data["response"] and "123" in data["response"]


def test_chat_emocion_y_metadatos_sin_texto(client, auth):
    h, uid = auth
    data = _chat(client, h, "Me siento muy ansioso por el examen de mañana")
    assert data["intent"] == "emotional_support" and data["emotion"] == "ansiedad"

    from app.database import SessionLocal
    from app.models.chat_message import ChatMessage
    db = SessionLocal()
    try:
        rows = db.query(ChatMessage).filter(ChatMessage.user_id == uid).all()
        assert len(rows) == 1
        assert rows[0].emotion == "ansiedad" and rows[0].sentiment == "negative"
        assert not any(c.name in ("text", "message", "content") for c in ChatMessage.__table__.columns)
    finally:
        db.close()
    chat = client.get("/api/analytics/chat", headers=h).json()
    assert chat["messages_sent"] == 1 and chat["top_intent"] == "Apoyo emocional"


def test_chat_no_persiste_que_hubo_crisis(client, auth):
    h, uid = auth
    _chat(client, h, "ya no quiero vivir")
    from app.database import SessionLocal
    from app.models.chat_message import ChatMessage
    db = SessionLocal()
    try:
        row = db.query(ChatMessage).filter(ChatMessage.user_id == uid).one()
        assert row.intent == "emotional_support" and row.emotion is None
    finally:
        db.close()


def test_chat_orden_explicita_sigue_creando_tareas(client, auth):
    h, _ = auth
    data = _chat(client, h, "crear tarea")
    assert data["intent"] not in ("emotional_support", "crisis_support")


def test_historial_del_chat_es_por_usuario(client, auth):
    from app.routes.assistant import ai_service
    h1, uid1 = auth
    _chat(client, h1, "hola")
    other = client.post("/api/auth/register", json={"email": "hist@test.com", "password": "Test-pass-123", "full_name": "H"})
    h2 = {"Authorization": f"Bearer {other.json()['access_token']}"}
    uid2 = other.json()["user"]["id"]
    _chat(client, h2, "buenos días")
    histories = ai_service.tensorflow_ai._histories
    texts1 = [m["text"] for m in histories[str(uid1)] if not m.get("is_ai")]
    texts2 = [m["text"] for m in histories[str(uid2)] if not m.get("is_ai")]
    assert "buenos días" not in texts1 and "hola" not in texts2
