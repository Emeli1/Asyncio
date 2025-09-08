import asyncio
import aiohttp
from more_itertools import chunked
from models import DbSession, Character, init_orm, close_orm

MAX_REQUESTS = 5

async def get_people(person_id, session):
    # Получаем данные о персонаже по ID
    async with (session.get(f'https://www.swapi.tech/api/people/{person_id}/')
                as response):
        json_data = await response.json()
        return json_data

async def insert_results(characters_list: list[dict]):
    async with DbSession() as session:
        properties = characters_list.get('result', {}).get('properties', {})  # извлекаем данные
        swapi_id = characters_list.get('result', {}).get('_id')
        orm_objects = [Character(swapi_id=swapi_id,
                                 birth_year=properties.get('birth_year'),
                                 eye_color=properties.get('eye_color'),
                                 gender=properties.get('gender'),
                                 hair_color=properties.get('hair_color'),
                                 homeworld=properties.get('homeworld'),
                                 mass=properties.get('mass'),
                                 name=properties.get('name'),
                                 skin_color=properties.get('skin_color')
                                 ) for character in characters_list]
        session.add_all(orm_objects)
        await session.commit

async def main():
    await asyncio.sleep(5)
    await init_orm()
    # Создаем асинхронную сессию для запросов к API
    async with aiohttp.ClientSession() as session:
        # Разбиваем список ID на чанки для параллельных запросов
        for chunk in chunked(range(1, 101), MAX_REQUESTS):
            coros = [get_people(person_id, session) for person_id in chunk]
            result = await asyncio.gather(*coros)
            insert_task = asyncio.create_task(insert_results(results))
        tasks = asyncio.all_tasks()
        current_task = asyncio.current_task()
        tasks.remove(current_task)
        for task in tasks:
            await task
        await close_orm()


main_coro = main()
asyncio.run(main_coro)