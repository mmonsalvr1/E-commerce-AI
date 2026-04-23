"""Configuracion de SQLAlchemy para persistencia en infraestructura.

Este modulo define engine, sesion, base declarativa y funciones auxiliares
de inicializacion para la aplicacion FastAPI.
"""

from collections.abc import Generator
import importlib

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./data/ecommerce_chat.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provee una sesion de base de datos para dependencias de FastAPI.

    Yields:
        Session: Sesion activa de SQLAlchemy para una solicitud.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Inicializa la base de datos y ejecuta carga inicial de datos.

    La funcion importa los modelos para registrar metadata, crea tablas y,
    si existe la funcion de seed, carga datos iniciales.

    Returns:
        None
    """
    # Importa modelos para registrar metadata antes de create_all.
    try:
        importlib.import_module("src.infrastructure.db.models")
    except ImportError:
        pass

    Base.metadata.create_all(bind=engine)

    # Carga datos iniciales si el módulo está disponible.
    try:
        init_data_module = importlib.import_module("src.infrastructure.db.init_data")
    except ImportError:
        return

    load_initial_data = getattr(init_data_module, "load_initial_data", None)
    if callable(load_initial_data):
        load_initial_data()
