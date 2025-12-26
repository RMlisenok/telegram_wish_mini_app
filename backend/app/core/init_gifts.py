from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recommendations import GiftSuggestion
from sqlalchemy import select

GIFT_DATA = [
    {
        "title": "Набор конструктора LEGO Technic",
        "description": "Сложная и детализированная модель для любителей инженерии.",
        "url": "https://market.yandex.ru/search?text=lego+technic",
        "tag_value": "лего",
        "category": "Игрушки"
    },
    {
        "title": "Подписка на онлайн-кинотеатр",
        "description": "Доступ к тысячам фильмов и сериалов в высоком качестве.",
        "url": "https://www.kinopoisk.ru/",
        "tag_value": "кино",
        "category": "Сервисы"
    },
    {
        "title": "Набор для выращивания растений",
        "description": "Все необходимое, чтобы вырастить собственный мини-сад на подоконнике.",
        "url": "https://ozon.ru/category/nabory-dlya-vyraschivaniya/",
        "tag_value": "сад и огород",
        "category": "Хобби"
    }
    #Добавить еще 30-50 позиций по всем тегам из INTEREST_TAGS
]


async def init_gifts(session: AsyncSession):
    check = await session.execute(select(GiftSuggestion).limit(1))
    if check.scalars().first():
        return

    for g in GIFT_DATA:
        session.add(GiftSuggestion(**g))

    await session.commit()