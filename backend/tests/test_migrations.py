"""Las migraciones de Alembic deben reproducir exactamente los modelos."""
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

import app.models  # noqa: F401
from app import db_migrate
from app.database import Base


def _usar_bd(monkeypatch, tmp_path, nombre):
    eng = create_engine(f"sqlite:///{tmp_path}/{nombre}.db")
    monkeypatch.setattr(db_migrate, "engine", eng)
    # env.py lee settings.DATABASE_URL: se apunta a la misma base temporal
    monkeypatch.setattr("app.config.settings.DATABASE_URL", str(eng.url))
    return eng


def test_migraciones_producen_el_esquema_de_los_modelos(monkeypatch, tmp_path):
    eng = _usar_bd(monkeypatch, tmp_path, "nueva")
    db_migrate.run_migrations()
    with eng.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == [], f"Los modelos cambiaron sin migración: {diff}"


def test_downgrade_deja_la_base_vacia(monkeypatch, tmp_path):
    eng = _usar_bd(monkeypatch, tmp_path, "down")
    db_migrate.run_migrations()
    command.downgrade(db_migrate._alembic_config(), "base")
    assert set(inspect(eng).get_table_names()) <= {"alembic_version"}


def test_base_creada_con_create_all_se_adopta_sin_perder_datos(monkeypatch, tmp_path):
    eng = _usar_bd(monkeypatch, tmp_path, "vieja")
    # Simula una base de antes de Alembic: sin la tabla chat_messages ni alembic_version
    Base.metadata.create_all(bind=eng, tables=[Base.metadata.tables["users"]])
    with eng.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO users (email, password_hash, full_name) VALUES ('a@b.c', 'x', 'A')"
        )
    db_migrate.run_migrations()
    tablas = set(inspect(eng).get_table_names())
    assert {"chat_messages", "tasks", "habits", "alembic_version"} <= tablas
    with eng.connect() as conn:
        assert conn.exec_driver_sql("SELECT email FROM users").scalar() == "a@b.c"
    # y una segunda ejecución es inocua
    db_migrate.run_migrations()
