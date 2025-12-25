from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.db import get_db
from app.core.security import (
    verify_jwt_token
)
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

logger = logging.getLogger(__name__)


router = APIRouter(prefix='/users', tags=['users'])
security = HTTPBearer()


@router.get('/me')
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_jwt_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token'
        )

    user_id = int(payload.get('sub'))
    user_service = UserService(db)
    user = await user_service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )

    return user


@router.post("/user_test_create")
async def create_test_user(
    db: AsyncSession = Depends(get_db)
):

    telegram_id = 120983122
    first_name = "KIKOS"
    last_name = "Admin"
    username = "Konstitution"
    photo_url = "saoidasd"

    user_service = UserService(db)
    user = await user_service.get_user_by_telegram_id(telegram_id)

    if not user:
        logger.error(f"Creating new user for telegram_id: {telegram_id}")
        user_create = UserCreate(
            telegram_id=telegram_id,
            name=f'{first_name} {last_name}'.strip(),
            photo=photo_url
        )
        user = await user_service.create_user(user_create)
    else:
        logger.error(f"Found existing user for telegram_id: {telegram_id}")
        user = UserResponse.model_validate(user)
