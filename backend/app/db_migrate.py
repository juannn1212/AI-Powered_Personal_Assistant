"""Aplica las migraciones de Alembic al arrancar la app."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database import Base, engine

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.attributes["configure_logger"] = False
    return cfg


def run_migrations() -> None:
    cfg = _alembic_config()
    tables = set(inspect(engine).get_table_names())
    if "users" in tables and "alembic_version" not in tables:
        # Base creada antes de Alembic con create_all: se completan las tablas que
        # falten (el comportamiento de antes) y se marca como al día, sin recrear nada.
        Base.metadata.create_all(bind=engine)
        command.stamp(cfg, "head")
    else:
        command.upgrade(cfg, "head")
