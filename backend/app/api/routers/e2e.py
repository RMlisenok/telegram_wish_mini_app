import os

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.core.db import AsyncSessionLocal


router = APIRouter(prefix="/e2e", tags=["e2e"])


def ensure_e2e_enabled() -> None:
    if os.getenv("E2E_MODE") != "1":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="E2E endpoints are disabled"
        )


@router.post("/reset")
async def reset_e2e_data():
    ensure_e2e_enabled()

    interest_tags = [
        "кино", "театр", "аниме", "мультфильмы", "фэнтези", "музыка",
        "музыкальные инструменты", "коллекционирование", "лего", "фотография",
        "книги", "научпоп", "саморазвитие", "иностранные языки",
        "компьютерные игры", "настольные игры", "рукоделие", "сад и огород",
        "домашний декор", "спорт", "танцы", "технологии и наука",
        "3Д-моделирование и графика", "робототехника", "программирование",
        "активный образ жизни", "путешествия", "кулинария и выпечка",
        "сладости", "сувениры", "цветы", "подарочные сертификаты",
        "алкоголь", "украшения", "косметика и парфюмерия",
    ]
    avoid_tags = [
        "сладости", "косметика и парфюмерия", "сувениры", "цветы",
        "алкоголь", "мягкие игрушки", "домашний декор", "книги",
        "подарочные сертификаты", "пластиковые сувениры",
        "ароматические свечи", "канцелярия", "магниты",
        "плакаты", "брелоки", "ежедневники", "статуэтки",
        "открытки", "календари",
    ]

    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(text(
                "TRUNCATE users, tags_forms, gift_suggestions "
                "RESTART IDENTITY CASCADE"
            ))

            tag_id = 1
            for tag in interest_tags:
                await session.execute(
                    text(
                        "INSERT INTO tags_forms (id, tag_value, type_tags) "
                        "VALUES (:id, :tag_value, true)"
                    ),
                    {"id": tag_id, "tag_value": tag}
                )
                tag_id += 1

            for tag in avoid_tags:
                await session.execute(
                    text(
                        "INSERT INTO tags_forms (id, tag_value, type_tags) "
                        "VALUES (:id, :tag_value, false)"
                    ),
                    {"id": tag_id, "tag_value": tag}
                )
                tag_id += 1

            await session.execute(text("""
                INSERT INTO users
                    (id, telegram_id, name, birth_date, photo, theme, text_size, show_sub)
                VALUES
                    (1, 900001, 'Test User', '1990-01-01', '', 'light', 'medium', true),
                    (2, 900002, 'Public E2E User', '1991-02-03', '', 'light', 'medium', true),
                    (5, 900005, 'Birth Required', NULL, '', 'light', 'medium', true)
            """))

            await session.execute(text("""
                INSERT INTO wishes
                    (id, user_id, name, photo, url_gift, price, currency, description,
                     is_booked, status_is_finished)
                VALUES
                    (1, 1, 'E2E existing wish', '', '', 0, NULL, '',
                     false, false)
            """))

            await session.execute(text("""
                INSERT INTO wishlists
                    (id, user_id, name, description, photo, typeprivacy)
                VALUES
                    (1, 1, 'E2E base wishlist', 'Base wishlist', '', 'public'),
                    (2, 2, 'E2E public wishlist', 'Public wishlist', '', 'public')
            """))

            await session.execute(text("""
                INSERT INTO wish_wishlist
                    (id, wish_id, wishlist_id, is_pinned, order_position)
                VALUES
                    (1, 1, 1, false, 0)
            """))

            await session.execute(text("""
                INSERT INTO user_forms (user_id, tag, detail, type_tag)
                VALUES
                    (2, 'книги', '', true),
                    (2, 'музыка', '', true),
                    (2, 'кино', '', true),
                    (2, 'алкоголь', '', false)
            """))

            await session.execute(text("""
                DO $$
                DECLARE seq text;
                BEGIN
                    seq := pg_get_serial_sequence('wishes', 'id');
                    IF seq IS NOT NULL THEN
                        PERFORM setval(seq, (SELECT COALESCE(MAX(id), 1) FROM wishes));
                    END IF;

                    seq := pg_get_serial_sequence('wishlists', 'id');
                    IF seq IS NOT NULL THEN
                        PERFORM setval(seq, (SELECT COALESCE(MAX(id), 1) FROM wishlists));
                    END IF;

                    seq := pg_get_serial_sequence('wish_wishlist', 'id');
                    IF seq IS NOT NULL THEN
                        PERFORM setval(seq, (SELECT COALESCE(MAX(id), 1) FROM wish_wishlist));
                    END IF;

                    seq := pg_get_serial_sequence('user_forms', 'id');
                    IF seq IS NOT NULL THEN
                        PERFORM setval(seq, (SELECT COALESCE(MAX(id), 1) FROM user_forms));
                    END IF;
                END $$;
            """))

    return {"status": "ok"}
