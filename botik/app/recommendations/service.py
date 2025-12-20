from app.recommendations.wb import get_wb_gifts
from app.recommendations.ozon import get_ozon_gifts
from app.recommendations.cache import (
    get_cached_recommendations,
    save_recommendations,
)

async def recommend_by_tag(user_id: int, tag: str) -> list[dict]:
    cached = await get_cached_recommendations(user_id, tag)
    if cached:
        return cached

    query = f"{tag} подарок"

    wb_items = await get_wb_gifts(query, limit=2)
    ozon_items = await get_ozon_gifts(query, limit=3)

    items = wb_items + ozon_items
    payload = [item.__dict__ for item in items]

    await save_recommendations(user_id, tag, payload)
    return payload
