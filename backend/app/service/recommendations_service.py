import random
from sqlalchemy import select, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recommendations import GiftSuggestion
from app.models.questionnaire import UserForm


class RecommendationService:
    @staticmethod
    async def get_recommendations(session: AsyncSession, target_user_id: int):
        stmt = select(UserForm).where(UserForm.user_id == target_user_id)
        result = await session.execute(stmt)
        user_forms = result.scalars().all()

        if not user_forms:
            return []

        interests = [f.tag_value for f in user_forms if f.type_tags is True]
        avoid = [f.tag_value for f in user_forms if f.type_tags is False]

        query = select(GiftSuggestion).where(
            and_(
                GiftSuggestion.tag_value.in_(interests),
                not_(GiftSuggestion.tag_value.in_(avoid))
            )
        )

        result = await session.execute(query)
        recommended_gifts = list(result.scalars().all())

        if len(recommended_gifts) < 5:
            already_selected_ids = [g.id for g in recommended_gifts]
            fallback_query = select(GiftSuggestion).where(
                and_(
                    not_(GiftSuggestion.tag_value.in_(avoid)),
                    not_(GiftSuggestion.id.in_(already_selected_ids))
                )
            ).limit(5 - len(recommended_gifts))

            fallback_result = await session.execute(fallback_query)
            recommended_gifts.extend(fallback_result.scalars().all())

        random.shuffle(recommended_gifts)
        return recommended_gifts[:5]

    async def generate_and_send_via_bot(db_factory, requester_id: int, target_id: int, bot):
        async with db_factory() as session:
            gifts = await RecommendationService.get_recommendations(session, target_id)

            if not gifts:
                await bot.send_message(requester_id, "К сожалению, не удалось подобрать подарки. Возможно, анкета друга не заполнена.")
                return

            message_text = f"🎁 <b>Подборка идей для подарка:</b>\n\n"

            for i, gift in enumerate(gifts, 1):
                message_text += f"{i}. <b>{gift.title}</b>\n"
                message_text += f"📝 {gift.description}\n"
                message_text += f"🔗 <a href='{gift.url}'>Посмотреть товар</a>\n\n"

            message_text += "<i>Нажмите 'Обновить', если хотите другие варианты.</i>"

            await bot.send_message(requester_id, message_text, parse_mode="HTML", disable_web_page_preview=False)