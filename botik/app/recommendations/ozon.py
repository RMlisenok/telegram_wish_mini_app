import aiohttp
from app.recommendations.schemas import GiftItem

OZON_URL = "https://www.ozon.ru/api/composer-api.bx/page/json/v2"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.ozon.ru",
}

async def get_ozon_gifts(query: str, limit: int = 3) -> list[GiftItem]:
    params = {
        "url": f"/search/?text={query}",
    }

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(OZON_URL, params=params, timeout=10) as resp:
            data = await resp.json()

    items = []
    widgets = data.get("widgetStates", {})

    for widget in widgets.values():
        if not isinstance(widget, dict):
            continue

        for item in widget.get("items", []):
            items.append(
                GiftItem(
                    title=item.get("title", "Без названия"),
                    price=item.get("price", {}).get("price"),
                    url="https://www.ozon.ru" + item.get("action", {}).get("link", ""),
                    source="ozon",
                )
            )
            if len(items) >= limit:
                return items

    return items
