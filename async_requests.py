import asyncio
import aiohttp
from more_itertools import chunked
from sqlalchemy.exc import IntegrityError

from models import DbSession, Character, init_orm, close_orm
from sqlalchemy import select

MAX_REQUESTS = 5

async def get_people(person_id, session):
    # Получаем данные о персонаже по ID
    async with (session.get(f'https://www.swapi.tech/api/people/{person_id}/')
                as response):
        json_data = await response.json()
        return json_data

async def insert_results(characters_list: list[dict]):
    async with DbSession() as session:
        orm_objects = []
        for character in characters_list:
            properties = character.get('result', {}).get('properties', {})  # извлекаем данные
            swapi_id = character.get('result', {}).get('_id')

            # Проверяем, существует ли уже запись с таким swapi_id
            query = select(Character).where(Character.swapi_id == swapi_id)
            existing_character = await session.scalar(query)

            if existing_character:
                print(f"Character with swapi_id {swapi_id} already exists. Skipping.")
                continue  # Пропускаем добавление, если запись уже существует

            objects = Character(swapi_id=swapi_id,
                                     birth_year=properties.get('birth_year'),
                                     eye_color=properties.get('eye_color'),
                                     gender=properties.get('gender'),
                                     hair_color=properties.get('hair_color'),
                                     homeworld=properties.get('homeworld'),
                                     mass=properties.get('mass'),
                                     name=properties.get('name'),
                                     skin_color=properties.get('skin_color')
                                     )
            orm_objects.append(objects)
        session.add_all(orm_objects)
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            print(f"Error during commit: {e}")

async def main():
    await asyncio.sleep(5)
    await init_orm()
    # Создаем асинхронную сессию для запросов к API
    async with aiohttp.ClientSession() as session:
        # Разбиваем список ID на чанки для параллельных запросов
        for chunk in chunked(range(1, 101), MAX_REQUESTS):
            results = await asyncio.gather(*(get_people(person_id, session) for person_id in chunk))
            await insert_results(results)
        await close_orm()


main_coro = main()
asyncio.run(main_coro)