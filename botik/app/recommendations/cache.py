from datetime import timedelta
from sqlalchemy import select, delete
from sqlalchemy.sql import func

from app.db.database import async_session
from app.db.models import RecommendationCache

CACHE_TTL_HOURS = 24

async def get_cached_recommendations(user_id: int, tag: str):
    async with async_session() as session:
        stmt = select(RecommendationCache).where(
            RecommendationCache.user_id == user_id,
            RecommendationCache.tag == tag,
            RecommendationCache.created_at > func.now() - timedelta(hours=CACHE_TTL_HOURS),
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return row.payload if row else None


async def save_recommendations(user_id: int, tag: str, payload: list[dict]):
    async with async_session() as session:
        await session.execute(
            delete(RecommendationCache).where(
                RecommendationCache.user_id == user_id,
                RecommendationCache.tag == tag,
            )
        )
        session.add(
            RecommendationCache(
                user_id=user_id,
                tag=tag,
                payload=payload,
            )
        )
        await session.commit()
