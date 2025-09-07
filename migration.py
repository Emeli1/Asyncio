import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
import os
import time
from dotenv import load_dotenv


load_dotenv()

# Определение базового класса для моделей
Base = declarative_base()

class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    swapi_id = Column(String(255), unique=True)
    birth_year = Column(String(255))
    eye_color = Column(String(255))
    gender = Column(String(255))
    hair_color = Column(String(255))
    homeworld = Column(String(255))
    mass = Column(String(255))
    name = Column(String(255))
    skin_color = Column(String(255))


async def create_table():
    # Задержка перед попыткой подключения к базе данных (в секундах)
    delay = 5
    print(f"Ожидание {delay} секунд перед подключением к базе данных...")
    time.sleep(delay)
    # Получаем параметры подключения из переменных окружения
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    db = os.getenv('POSTGRES_DB')
    host = 'localhost'
    port = '8888'
    DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    engine = create_async_engine(DATABASE_URL, echo=True)
    # Создаём все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(create_table())
