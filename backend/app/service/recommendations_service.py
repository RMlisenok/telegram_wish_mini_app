
class RecommendationService:
    async def get_recommendations(self, target_user_id: int):

        questionnaire = await self.repo.get_user_questionnaire(target_user_id)

        if not questionnaire or not questionnaire.interests:
            return await self.get_universal_recommendations()  # Сценарий 2 (FS-10.4)

        interest_tags = [item.tag for item in questionnaire.interests]
        avoid_tags = [item.tag for item in questionnaire.avoid_gifts]

        recommendations = await self.market_api.search(
            include=interest_tags,
            exclude=avoid_tags,
            limit=5
        )
        return recommendations