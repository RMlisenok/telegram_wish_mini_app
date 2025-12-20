import asyncio
from dotenv import load_dotenv

load_dotenv()

from app.db.database import engine
# from app.db.base import Base

# ВАЖНО: импортируем ВСЕ модели
from app.users.models import User
from app.recommendations.models import RecommendationCache


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(main())
