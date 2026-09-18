"""Motor de base de datos. `engine`/`SessionLocal` se configuran con `configure()`, llamada una
vez con la env var al importar este módulo y de nuevo por los tests (con un archivo temporal)
para aislar cada test sin tener que reimportar el resto de los módulos de la app — reimportar
`app.domain.errors` por test rompe la identidad de las clases de excepción entre el código y los
`except` de los tests."""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

engine = None
SessionLocal: sessionmaker | None = None


class Base(DeclarativeBase):
    pass


def configure(db_path: str | None = None) -> None:
    global engine, SessionLocal
    path = db_path or os.environ.get("TALLER_DB_PATH", "taller.db")
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


configure()


def init_db() -> None:
    # Importa los modelos ORM para que queden registrados en Base.metadata antes de create_all.
    from app.adapters.outbound.persistence import orm_models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
