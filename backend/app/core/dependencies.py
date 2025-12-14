from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.db import get_db
from app.core.security import verify_jwt_token
from app.services.user_service import UserService
from app.models.user import User


logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        token = credentials.credentials

        payload = verify_jwt_token(token)

        if not payload:
            logger.warning(f'invalid JWT Token: {token[:20]}...')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )

        user_id = int(payload.get('sub'))

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invelid token payload'
            )
        user_service = UserService(db)
        user = await user_service.get_user(user_id)

        if not user:
            logger.warning(f'User not found: {user_id}')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found'
            )

        return user

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f'Erro in get_current_user: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error'
        )
