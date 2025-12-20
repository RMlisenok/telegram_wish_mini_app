import asyncio
from app.db.database import engine, Base
from app.db import models  # noqa

async def run():
    async with engine.begin() as conn:
        print("TABLES:", Base.metadata.tables.keys())
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(run())
