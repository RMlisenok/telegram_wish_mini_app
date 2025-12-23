from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.db import get_db
from app.core.security import (
    verify_jwt_token,
    verify_tg_init_data,
    create_jwt_token
)
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.models.user import User

logger = logging.getLogger(__name__)


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/telegram')
async def auth_telegram(
    auth_data: dict,
    db: AsyncSession = Depends(get_db)
):
    init_data = auth_data.get('initData')
    if not init_data:
        logger.error("No initData in request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid init data'
        )

    telegram_user = auth_data.get('user')
    if not telegram_user:
        logger.error("No user in request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid user data'
        )

    if not verify_tg_init_data(init_data=init_data):
        logger.error("Telegram signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Telegram signature'
        )

    telegram_id = telegram_user.get('id')
    first_name = telegram_user.get('first_name', '')
    last_name = telegram_user.get('last_name', '')
    username = telegram_user.get('username', '')
    photo_url = telegram_user.get('photo_url', '')

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

    token_data = {
        'sub': str(user.id),
        'telegram_id': str(telegram_id),
        'username': username
    }

    try:
        access_token = create_jwt_token(token_data)
    except Exception as e:
        logger.error(f"Error creating JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error creating token'
        )
    return {
        'success': True,
        'token': access_token,
        'token_type': 'bearer',
        'user': user
    }


@router.post('/refresh')
async def refresh_token(
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

    new_oken_data = {
        'sub': str(user.id),
        'telegram_id': payload.get('telegram_id'),
        'username': payload.get('username')
    }

    new_access_token = create_jwt_token(new_oken_data)

    return {
        'success': True,
        'token': new_access_token,
        'token_type': 'bearer',
    }
