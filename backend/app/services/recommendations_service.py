import random
import logging
from sqlalchemy import select, and_, not_
from sqlalchemy import func
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recommendations import GiftSuggestion, RecommendationLog
from app.models.questionnaire import UserForm
from app.models.user import User
from aiogram import types

logger = logging.getLogger(__name__)

class RecommendationService:
    @staticmethod
    async def get_recommendations(session: AsyncSession, target_user_id: int):
        """
        Получение списка подарков на основе анкеты пользователя (ID из БД).
        """
        stmt = select(UserForm).where(UserForm.user_id == target_user_id)
        result = await session.execute(stmt)
        user_forms = result.scalars().all()

        if not user_forms:
            # Если анкеты нет совсем, возвращаем пустой список (обработаем в основном методе)
            return []

        interests = [f.tag.lower() for f in user_forms if f.type_tag is True]
        avoid = [f.tag.lower() for f in user_forms if f.type_tag is False]

        # Ищем подарки, подходящие под интересы и не входящие в исключения
        query = select(GiftSuggestion).where(
            and_(
                func.lower(GiftSuggestion.tag_value).in_(interests),
                not_(func.lower(GiftSuggestion.tag_value).in_(avoid))
            )
        )

        result = await session.execute(query)
        recommended_gifts = list(result.scalars().all())

        # Если подарков по интересам мало, добираем популярными (но не из списка "avoid")
        if len(recommended_gifts) < 5:
            already_selected_ids = [g.id for g in recommended_gifts]

            fallback_query = select(GiftSuggestion).where(
                not_(func.lower(GiftSuggestion.tag_value).in_(avoid))
            )

            if already_selected_ids:
                fallback_query = fallback_query.where(
                    not_(GiftSuggestion.id.in_(already_selected_ids))
                )

            fallback_query = fallback_query.limit(5 - len(recommended_gifts))
            fallback_result = await session.execute(fallback_query)
            recommended_gifts.extend(fallback_result.scalars().all())

        random.shuffle(recommended_gifts)
        return recommended_gifts[:5]

    @staticmethod
    async def generate_and_send_via_bot(
        db_factory, requester_id: int, target_id: int, bot
    ):
        """
        Генерация подборки и отправка через бота.
        requester_id: системный ID того, кто запрашивает.
        target_id: системный ID того, кому подбираем подарки.
        """
        async with db_factory() as session:
            try:
                # 1. Получаем данные обоих пользователей (чтобы знать их Telegram ID)
                users_stmt = select(User).where(User.id.in_([requester_id, target_id]))
                users_result = await session.execute(users_stmt)
                users_map = {u.id: u for u in users_result.scalars().all()}

                requester = users_map.get(requester_id)
                target_user = users_map.get(target_id)

                if not requester:
                    logger.error(f"Requester with ID {requester_id} not found in DB")
                    return

                # Если целевой пользователь не найден
                if not target_user:
                    await bot.send_message(requester.telegram_id, "❌ Пользователь для подбора подарков не найден.")
                    return

                # 2. Проверка лимита (5 запросов в сутки) по системному ID
                one_day_ago = datetime.now() - timedelta(days=1)
                limit_stmt = select(func.count(RecommendationLog.id)).where(
                    and_(
                        RecommendationLog.user_id == requester_id,
                        RecommendationLog.created_at >= one_day_ago
                    )
                )
                count_result = await session.execute(limit_stmt)
                if count_result.scalar() >= 5:
                    await bot.send_message(
                        requester.telegram_id,
                        "⚠️ Вы уже запрашивали подборку 5 раз за последние 24 часа."
                    )
                    return

                # 3. Получаем анкету и рекомендации
                form_stmt = select(UserForm).where(UserForm.user_id == target_id)
                form_result = await session.execute(form_stmt)
                user_forms = form_result.scalars().all()

                has_questionnaire = any(f.type_tag is True for f in user_forms)
                gifts = await RecommendationService.get_recommendations(session, target_id)

                # 4. Логируем запрос в БД
                new_log = RecommendationLog(user_id=requester_id)
                session.add(new_log)
                await session.commit()

                # 5. Формируем текст сообщения
                if has_questionnaire:
                    message_text = f"🎁 <b>Подборка для {target_user.name}:</b>\n\n"
                else:
                    message_text = f"🎁 <b>Популярные идеи для {target_user.name}:</b>\n"
                    message_text += "<i>(Анкета друга пуста, показываем общие рекомендации)</i>\n\n"

                if gifts:
                    for i, gift in enumerate(gifts, 1):
                        message_text += f"{i}. <b>{gift.title}</b>\n"
                        if gift.description:
                            message_text += f"{gift.description}\n"
                        message_text += f"🔗 <a href='{gift.url}'>Посмотреть</a>\n\n"
                else:
                    await bot.send_message(requester.telegram_id, "Не удалось найти подходящие подарки.")
                    return

                # Добавляем инфо об интересах
                interests_list = [f for f in user_forms if f.type_tag is True]
                avoid_list = [f for f in user_forms if f.type_tag is False]

                if interests_list or avoid_list:
                    message_text += "───────────────────\n"
                    if interests_list:
                        tags = [f"#{i.tag.replace(' ', '_')}" for i in interests_list]
                        message_text += f"<b>Интересы:</b> {', '.join(tags)}\n"
                    if avoid_list:
                        tags = [f"{i.tag}" for i in avoid_list]
                        message_text += f"<b>Не дарить:</b> {', '.join(tags)}\n"

                # 6. Кнопка обновления (передаем системный ID целевого пользователя)
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(
                        text="🔄 Обновить список",
                        callback_data=f"refresh_rec_{target_id}"
                    )]
                ])

                # 7. ОТПРАВКА на настоящий telegram_id
                await bot.send_message(
                    requester.telegram_id,
                    message_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )

            except Exception as e:
                logger.error(f"Ошибка в RecommendationService: {e}")
                # Пытаемся уведомить пользователя, если это возможно
                try:
                    # Если мы успели найти requester, шлем ему на tg_id
                    await bot.send_message(requester.telegram_id, "Произошла ошибка при создании подборки.")
                except:
                    pass