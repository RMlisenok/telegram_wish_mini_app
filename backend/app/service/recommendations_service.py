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