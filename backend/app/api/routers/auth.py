from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import (
    verify_jwt_token,
    verify_tg_init_data,
    create_jwt_token
)
from app.schemas.user import UserCreate, UserResponse
from telegram_wish_mini_app.backend.app.services.user_service import UserService
# from app.models.user import User


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/telegram')
async def auth_telegram(
    auth_data: dict,
    db: AsyncSession = Depends(get_db)
):
    init_data = auth_data.get('initData')
    telegram_user = auth_data.get('user')

    if not verify_tg_init_data(init_data=init_data):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Telegram signature'
        )

    telegram_id = telegram_user.get('id')
    first_name = telegram_user.get('first_name', '')
    last_name = telegram_user.get('last_name', '')
    username = telegram_user.get('username', '')
    photo_url = telegram_user.get('photo_url', '')

    user = await UserService.get_user_by_telegram_id(db, telegram_id)

    if not user:
        user_create = UserCreate(
            telegram_id=telegram_id,
            name=f'{first_name} {last_name}'.strip(),
            photo=photo_url
        )
        user = await UserService.create_user(db, user_create)
    else:
        user = UserResponse.model_validate(user)

    token_data = {
        'sub': str(user.id),
        'telegram_id': str(telegram_id),
        'username': username
    }
    access_token = create_jwt_token(token_data)

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
    user = await UserService.get_user(db, user_id)

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
    user = await UserService.get_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )

    return user
