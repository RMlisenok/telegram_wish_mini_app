import aiohttp
from app.recommendations.schemas import GiftItem

WB_URL = "https://search.wb.ru/exactmatch/ru/common/v4/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

async def get_wb_gifts(query: str, limit: int = 2) -> list[GiftItem]:
    params = {
        "query": query,
        "page": 1,
        "limit": limit,
    }

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(WB_URL, params=params, timeout=10) as resp:
            data = await resp.json()

    products = data.get("data", {}).get("products", [])
    items = []

    for p in products[:limit]:
        items.append(
            GiftItem(
                title=p["name"],
                price=int(p["priceU"] / 100),
                url=f"https://www.wildberries.ru/catalog/{p['id']}/detail.aspx",
                source="wb",
            )
        )

    return items
