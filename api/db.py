"""
db.py – Inicializace SQLAlchemy a databázového enginu.

Používáme SQLite pro vývoj a testování.
V produkci lze přepnout na PostgreSQL bez změny modelů.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Cesta k databázovému souboru
DATABASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(DATABASE_DIR, "multipong.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base pro všechny modely
Base = declarative_base()


def init_db():
    """Vytvoří všechny tabulky v databázi."""
    # Importuj všechny modely aby byly registrovány u Base
    from api import models
    
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency injection pro FastAPI – vrátí databázovou session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
