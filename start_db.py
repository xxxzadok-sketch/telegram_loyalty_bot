import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, Numeric
from config import DATABASE_URL

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String(50)),
    Column("last_name", String(50)),
    Column("phone", String(20)),
    Column("bonus_points", Numeric, default=100)
)

async def init_db():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
    print("Database initialized!")
