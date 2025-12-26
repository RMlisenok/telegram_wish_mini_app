from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access_request import AccessRequest
from app.repositories.access_request_repository import AccessRequestRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.access_request import (
    AccessRequestCreate,
    AccessRequestResponse,
    AccessRequestWithDetails,
    UpdateAccessRequest
)


class AccessRequestService():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.rep_access = AccessRequestRepository(session)
        self.rep_user = UserRepository(session)
        self.rep_wishlist = WishlistRepository(session)
