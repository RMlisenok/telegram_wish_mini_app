import random
import logging
from sqlalchemy import select, and_, not_
from sqlalchemy import func
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recommendations import GiftSuggestion
from app.models.questionnaire import UserForm
from aiogram import types
import sys
import os

from app.models.recommendations import RecommendationLog


logger = logging.getLogger(__name__)


class RecommendationService:
    @staticmethod
    async def get_recommendations(session: AsyncSession, target_user_id: int):
        stmt = select(UserForm).where(UserForm.user_id == target_user_id)
        result = await session.execute(stmt)
        user_forms = result.scalars().all()

        if not user_forms:
            return []

        interests = [f.tag.lower() for f in user_forms if f.type_tag is True]
        avoid = [f.tag.lower() for f in user_forms if f.type_tag is False]

        query = select(GiftSuggestion).where(
            and_(
                func.lower(GiftSuggestion.tag_value).in_(interests),
                not_(func.lower(GiftSuggestion.tag_value).in_(avoid))
            )
        )

        result = await session.execute(query)
        recommended_gifts = list(result.scalars().all())

        if len(recommended_gifts) < 5:
            already_selected_ids = [g.id for g in recommended_gifts]

            fallback_query = select(GiftSuggestion).where(
                not_(func.lower(GiftSuggestion.tag_value).in_(avoid))
            )

            if already_selected_ids:
                fallback_query = fallback_query.where(not_(GiftSuggestion.id.in_(already_selected_ids)))

            fallback_query = fallback_query.limit(5 - len(recommended_gifts))

            fallback_result = await session.execute(fallback_query)
            recommended_gifts.extend(fallback_result.scalars().all())

        random.shuffle(recommended_gifts)
        return recommended_gifts[:5]

    @staticmethod
    async def generate_and_send_via_bot(db_factory, requester_id: int, target_id: int, bot):
        async with db_factory() as session:
            try:
                one_day_ago = datetime.now() - timedelta(days=1)
                limit_stmt = select(func.count(RecommendationLog.id)).where(
                    and_(
                        RecommendationLog.user_id == requester_id,
                        RecommendationLog.created_at >= one_day_ago
                    )
                )
                count_result = await session.execute(limit_stmt)
                request_count = count_result.scalar()

                if request_count >= 5:  # Твой лимит по ТЗ
                    await bot.send_message(
                        requester_id,
                        "⚠️ Вы уже запрашивали подборку 5 раз за сегодня. \n"
                        "Новые рекомендации будут доступны через 3 часа."
                    )
                    return

                from app.models.user import User
                user_stmt = select(User).where(User.telegram_id == target_id)
                user_result = await session.execute(user_stmt)
                target_user = user_result.scalar_one_or_none()

                if not target_user:
                    await bot.send_message(requester_id, "❌ Пользователь не найден.")
                    return

                stmt = select(UserForm).where(UserForm.user_id == target_user.id)
                result = await session.execute(stmt)
                user_forms = result.scalars().all()

                has_questionnaire = any(f.type_tag is True for f in user_forms)

                gifts = await RecommendationService.get_recommendations(session, target_user.id)

                new_log = RecommendationLog(user_id=requester_id)
                session.add(new_log)
                await session.commit()

                if has_questionnaire:
                    message_text = f"🎁 <b>Подборка для {target_user.name}:</b>\n\n"
                else:
                    message_text = f"🎁 <b>Вот 5 популярных подарков для {target_user.name}:</b>\n"
                    message_text += "<i>(Анкета друга не заполнена, показываем универсальные идеи)</i>\n\n"

                if gifts:
                    for i, gift in enumerate(gifts, 1):
                        message_text += f"{i}. <b>{gift.title}</b>\n"
                        message_text += f"{gift.description}\n"
                        message_text += f"🔗 <a href='{gift.url}'>Посмотреть</a>\n\n"
                else:
                    await bot.send_message(requester_id, "Сервис рекомендаций временно недоступен. Попробуйте позже.")
                    return

                interests_list = [f for f in user_forms if f.type_tag is True]
                avoid_list = [f for f in user_forms if f.type_tag is False]

                if interests_list or avoid_list:
                    message_text += "───────────────────\n"
                    if interests_list:
                        items = [f"{i.tag}{' (' + i.detail + ')' if i.detail else ''}" for i in interests_list]
                        message_text += f"<b>Предпочтения:</b> {', '.join(items)}\n"
                    if avoid_list:
                        items = [f"{i.tag}{' (' + i.detail + ')' if i.detail else ''}" for i in avoid_list]
                        message_text += f"<b>Не дарить:</b> {', '.join(items)}\n"

                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(
                        text="🔄 Обновить подборку",
                        callback_data=f"refresh_rec_{target_id}"
                    )]
                ])

                await bot.send_message(
                    requester_id,
                    message_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )

            except Exception as e:
                logger.error(f"Ошибка при генерации рекомендаций: {e}")
                await bot.send_message(requester_id, "Сервис рекомендаций временно недоступен. Попробуйте позже.")

    # @staticmethod
    # async def generate_and_send_via_bot(db_factory, requester_id: int, target_id: int, bot):
    #     async with db_factory() as session:
    #         try:
    #             from app.models.user import User
    #             user_stmt = select(User).where(User.telegram_id == target_id)
    #             user_result = await session.execute(user_stmt)
    #             user = user_result.scalar_one_or_none()
    #
    #             if not user:
    #                 logger.error(f"Пользователь с telegram_id {target_id} не найден в БД")
    #                 return
    #
    #             internal_id = user.id
    #
    #             stmt = select(UserForm).where(UserForm.user_id == internal_id)
    #             result = await session.execute(stmt)
    #             user_forms = result.scalars().all()
    #
    #             details = [f.detail for f in user_forms if f.detail]
    #
    #             gifts = await RecommendationService.get_recommendations(session, internal_id)
    #
    #             message_text = "🎁 <b>Подборка идей для подарка:</b>\n\n"
    #
    #             if gifts:
    #                 for i, gift in enumerate(gifts, 1):
    #                     message_text += f"{i}. <b>{gift.title}</b>\n"
    #                     message_text += f"📝 {gift.description}\n"
    #                     message_text += f"🔗 <a href='{gift.url}'>Посмотреть</a>\n\n"
    #             else:
    #                 message_text += "<i>Хм, не удалось найти конкретных подарков, но посмотрите на уточнения ниже:</i>\n\n"
    #
    #             interests_list = [f for f in user_forms if f.type_tag is True]
    #             avoid_list = [f for f in user_forms if f.type_tag is False]
    #
    #             if interests_list:
    #                 message_text += "✅ <b>Предпочтения:</b>\n"
    #                 for item in interests_list:
    #                     detail_str = f" ({item.detail})" if item.detail else ""
    #                     message_text += f"• {item.tag}{detail_str}\n"
    #                 message_text += "\n"
    #
    #             if avoid_list:
    #                 message_text += "❌ <b>Не дарить:</b>\n"
    #                 for item in avoid_list:
    #                     detail_str = f" ({item.detail})" if item.detail else ""
    #                     message_text += f"• {item.tag}{detail_str}\n"
    #                 message_text += "\n"
    #
    #             await bot.send_message(requester_id, message_text, parse_mode="HTML", disable_web_page_preview=True)

