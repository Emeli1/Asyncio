import os

from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "12345")
POSTGRES_USER = os.getenv("POSTGRES_USER", "swapi")
POSTGRES_DB = os.getenv("POSTGRES_DB", "swapi")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(PG_DSN)
DbSession = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass

class Character(Base):
    __tablename__ = 'characters'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    swapi_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    birth_year: Mapped[str] = mapped_column(String, nullable=True)
    eye_color: Mapped[str] = mapped_column(String, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    hair_color: Mapped[str] = mapped_column(String, nullable=True)
    homeworld: Mapped[str] = mapped_column(String, nullable=True)
    mass: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    skin_color: Mapped[str] = mapped_column(String, nullable=True)


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
