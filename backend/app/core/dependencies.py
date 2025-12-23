from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Optional

from .db import get_db
from .security import verify_jwt_token
from services.user_service import UserService
from models.user import User

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:

    token = credentials.credentials
    payload = verify_jwt_token(token)

    if not payload:
        logger.warning(f'Invalid JWT Token attempt')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )

    user_id_str = payload.get('sub')
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload: missing sub'
        )

    try:
        return int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid user ID format in token'
        )


async def get_current_user(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
) -> User:

    user_service = UserService(db)
    user = await user_service.get_user(user_id)

    if not user:
        logger.warning(f'User not found in database: {user_id}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )

    return user