import os
from collections.abc import Generator
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

variables_requeridas = {
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}

faltantes = [
    nombre
    for nombre, valor in variables_requeridas.items()
    if not valor
]

if faltantes:
    raise RuntimeError(
        f"Faltan variables de base de datos: {', '.join(faltantes)}"
    )

usuario_seguro = quote_plus(DB_USER)
contrasena_segura = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql+psycopg://{usuario_seguro}:{contrasena_segura}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    },
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def obtener_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def comprobar_conexion() -> str:
    with engine.connect() as conexion:
        version = conexion.execute(
            text("SELECT version();")
        ).scalar_one()

    return version