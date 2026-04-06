from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.questionnaire import TagForm
from app.core.db import async_engine

INTEREST_TAGS = [
    "кино", "театр", "аниме", "мультфильмы", "фэнтези", "музыка",
    "музыкальные инструменты", "коллекционирование", "лего", "фотография",
    "книги", "научпоп", "саморазвитие", "иностранные языки",
    "компьютерные игры", "настольные игры", "рукоделие", "сад и огород",
    "домашний декор", "спорт", "танцы", "технологии и наука",
    "3Д-моделирование и графика", "робототехника",
    "программирование", "активный образ жизни", "путешествия",
    "кулинария и выпечка", "сладости", "сувениры", "цветы",
    "подарочные сертификаты", "алкоголь", "украшения", "косметика и парфюмерия"
]

AVOID_TAGS = [
    "сладости", "косметика и парфюмерия", "сувениры", "цветы", "алкоголь",
    "мягкие игрушки", "домашний декор", "книги", "подарочные сертификаты"
]


async def init_tags(session: AsyncSession):
    # async with AsyncSession(bind=async_engine) as session:
    try:
        check = await session.execute(select(TagForm).limit(1))
        if check.scalars().first():
            return

        for t in INTEREST_TAGS:
            session.add(TagForm(tag_value=t, type_tags=True))

        for t in AVOID_TAGS:
            session.add(TagForm(tag_value=t, type_tags=False))

        await session.commit()
        print("✅ Теги успешно инициализированы")

    except Exception as e:
        await session.rollback()
        print(f'❌ ERROR в init_tags - {e}')
        raise
