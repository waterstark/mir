import os
import asyncio
import asyncpg
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('../.env'))


async def execute_queries():
    conn = await asyncpg.connect(
        database=os.getenv('DB_NAME', default="postgres"),
        user=os.getenv('DB_USER', default="postgres"),
        password=os.getenv('DB_PASS', default="postgres"),
        host=os.getenv('DB_HOST', default="localhost"),
        port=int(os.getenv('DB_PORT', default="5432"))
    )

    tables = os.listdir('tables')

    for table in tables:
        with open(f'test_data/tables/{table}', 'r', encoding='UTF-8') as file:
            query = file.read()
        await conn.execute(query)

    await conn.close()


asyncio.get_event_loop().run_until_complete(execute_queries())
