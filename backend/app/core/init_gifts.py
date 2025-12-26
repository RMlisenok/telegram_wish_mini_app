from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.recommendations import GiftSuggestion

GIFT_DATA = [
    # Категория: ЛЕГО / Хобби
    {"tag_value": "лего", "title": "LEGO Technic: Гоночный автомобиль", "category": "Игрушки",
     "description": "Сложная модель для тех, кто ценит инженерную точность и детализацию.",
     "url": "https://www.wildberries.ru/catalog/0/search.aspx?search=lego+technic"},

    {"tag_value": "лего", "title": "LEGO Architecture: Города мира", "category": "Декор",
     "description": "Элегантная серия для украшения интерьера и любителей путешествий.",
     "url": "https://www.ozon.ru/category/lego-architecture-7164/"},

    # Категория: КНИГИ
    {"tag_value": "книги", "title": "Подарочное издание классики в коже", "category": "Книги",
     "description": "Красивое издание любимого автора, которое станет украшением библиотеки.",
     "url": "https://www.wildberries.ru/catalog/0/search.aspx?search=книга+подарочное+издание"},

    # Категория: КОСМЕТИКА
    {"tag_value": "косметика и парфюмерия", "title": "Набор корейского ухода за кожей", "category": "Красота",
     "description": "Популярный комплексный уход: маски, сыворотки и патчи.",
     "url": "https://www.ozon.ru/category/nabory-kosmetiki-dlya-uhoda-za-litsom-6559/"},

    # Категория: КОМПЬЮТЕРНЫЕ ИГРЫ
    {"tag_value": "компьютерные игры", "title": "Механическая игровая клавиатура", "category": "Техника",
     "description": "Надежный девайс с настраиваемой подсветкой для геймеров.",
     "url": "https://www.wildberries.ru/catalog/0/search.aspx?search=механическая+клавиатура+игровая"},

    # Категория: САМОРАЗВИТИЕ / НАУЧПОП
    {"tag_value": "научпоп", "title": "Книга 'Sapiens: Краткая история человечества'", "category": "Книги",
     "description": "Мировой бестселлер об истории развития нашего вида.",
     "url": "https://www.wildberries.ru/catalog/0/search.aspx?search=юваль+ной+харири+sapiens"},

    # Категория: ДОМАШНИЙ ДЕКОР
    {"tag_value": "домашний декор", "title": "Ароматическая свеча из соевого воска", "category": "Уют",
     "description": "Стильный аксессуар с ароматом табака, ванили или свежескошенной травы.",
     "url": "https://www.ozon.ru/category/aromaticheskie-svechi-15064/"},

    # Категория: СПОРТ
    {"tag_value": "спорт", "title": "Набор для фитнеса (эспандеры и коврик)", "category": "Спорт",
     "description": "Компактный набор для тренировок дома или на свежем воздухе.",
     "url": "https://www.wildberries.ru/catalog/0/search.aspx?search=набор+для+фитнеса+дома"},

    # Категория: КУЛИНАРИЯ
    {"tag_value": "кулинария и выпечка", "title": "Кулинарный термометр для мяса и сладостей", "category": "Кухня",
     "description": "Незаменимый гаджет для идеальной прожарки и кондитерских шедевров.",
     "url": "https://www.ozon.ru/category/kulinarnye-termometry-14569/"},

    # Категория: АНИМЕ
    {"tag_value": "аниме", "title": "Коллекционная фигурка персонажа (Funko POP)", "category": "Хобби",
     "description": "Миниатюрная копия любимого героя в узнаваемом стиле.",
     "url": "https://www.wildberries.ru/catalog/0/search.aspx?search=фигурка+funko+pop+аниме"},

    # Категория: ТЕХНОЛОГИИ
    {"tag_value": "технологии и наука", "title": "Портативный внешний аккумулятор (Power Bank)", "category": "Гаджеты",
     "description": "Мощная зарядка, чтобы всегда оставаться на связи в поездках.",
     "url": "https://www.wildberries.ru/catalog/0/search.aspx?search=power+bank+20000mah"},
]


async def init_gifts(session: AsyncSession):
    check = await session.execute(select(GiftSuggestion).limit(1))
    if check.scalars().first():
        print("База подарков уже наполнена.")
        return

    for g in GIFT_DATA:
        session.add(GiftSuggestion(**g))

    await session.commit()
    print(f"Успешно добавлено {len(GIFT_DATA)} идей для подарков.")