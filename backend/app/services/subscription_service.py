from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession


class SubscriptionService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session
