import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from more_itertools import chunked
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # Асинхронный движок
from sqlalchemy import MetaData, Table, engine

load_dotenv()

MAX_REQUESTS = 5

# Получаем переменные окружения
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
db = os.getenv('POSTGRES_DB')
host = 'localhost'
port = '5432'

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

engine = create_async_engine(DATABASE_URL)

async def get_people(person_id, session):
    # Получаем данные о персонаже по ID
    async with (session.get(f'https://www.swapi.tech/api/people/{person_id}/')
                as response):
        json_data = await response.json()
        return json_data

async def save_character(character, character_table):
    # Сохраняем данные о персонаже в базу данных
    properties = character.get('result', {}).get('properties', {})   # извлекаем данные
    swapi_id = character.get('result', {}).get('_id')
    values = {
        'swapi_id': swapi_id,
        'birth_year': properties.get('birth_year'),
        'eye_color': properties.get('eye_color'),
        'gender': properties.get('gender'),
        'hair_color': properties.get('hair_color'),
        'homeworld': properties.get('homeworld'),
        'mass': properties.get('mass'),
        'name': properties.get('name'),
        'skin_color': properties.get('skin_color')
    }

    # Подготавливаем запрос на вставку данных, с обработкой конфликтов
    insert_stmt = insert(character_table).values(values).on_conflict_do_nothing(index_elements=['swapi_id'])
    # Выполняем запрос на вставку данных
    async with AsyncSession(engine) as session:
        await session.execute(insert_stmt)   # Используем асинхронный сеанс
        await session.commit()


async def main():
    # Отражаем структуру таблицы из базы данных
    metadata = MetaData()
    character_table = Table('characters', metadata, autoload_with=engine)

    # Создаем асинхронную сессию для запросов к API
    async with aiohttp.ClientSession() as session:
        # Разбиваем список ID на чанки для параллельных запросов
        for chunk in chunked(range(1, 101), MAX_REQUESTS):
            coros = [get_people(person_id, session) for person_id in chunk]
            result = await asyncio.gather(*coros)
            # Сохраняем данные персонажей в базу данных
            for character in result:
                await save_character(character, engine, character_table)


if __name__ == '__main__':
    asyncio.run(main())