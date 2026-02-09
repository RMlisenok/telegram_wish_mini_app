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
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.models.user import User
from app.services.photo_update_service import PhotoUpdateService
from app.core.s3_client import S3Client
from app.core.dependencies import get_client_s3

logger = logging.getLogger(__name__)


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post("/test")
async def auth_test(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_telegram_id(user_data.telegram_id)
    if not user:
        user = await user_service.create_user(user_data)
    token_data = {
        "sub": str(user.id),
        "tg_id": user.telegram_id,
        "name": user.name
    }

    try:
        token = create_jwt_token(token_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error create token: {str(e)}"
        )

    return {
        'success': True,
        'token': token,
        'token_type': 'bearer',
        'user': user
    }


@router.post('/telegram')
async def auth_telegram(
    auth_data: dict,
    db: AsyncSession = Depends(get_db),
    s3_client: S3Client = Depends(get_client_s3)
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

    photo_service = PhotoUpdateService(s3_client)
    if not user:
        logger.error(f"Creating new user for telegram_id: {telegram_id}")

        final_photo_url = photo_url
        if final_photo_url:
            try:
                migrated_url = await photo_service.migrate_telegram_photo(photo_url)
                if migrated_url:
                    final_photo_url = migrated_url
                else:
                    logger.error(f"Error, use old photo: {final_photo_url}")
                    final_photo_url = photo_url
            except Exception as e:
                logger.error(f"Error migrate photo: {e}")

        user_create = UserCreate(
            telegram_id=telegram_id,
            name=f'{first_name} {last_name}'.strip(),
            photo=final_photo_url or ""
        )
        user = await user_service.create_user(user_create)
    else:
        logger.error(f"Found existing user for telegram_id: {telegram_id}")
        user = UserResponse.model_validate(user)
        final_photo_url = user.photo

        if photo_url and photo_url == user.photo:
            logger.error(f"START REPLACE PHOTO: {telegram_id}")
            if photo_url:
                try:
                    logger.error(f"START FUNCTION MIGRATE: {photo_url}")
                    migrated_url = await photo_service.migrate_telegram_photo(photo_url)
                    logger.error(f"END FUNCTION MIGRATE: {migrated_url}")
                    if migrated_url:
                        logger.error(f"NEW PHOTO")
                        final_photo_url = migrated_url
                    else:
                        logger.error(f"Error, use old photo: {final_photo_url}")
                        final_photo_url = photo_url
                except Exception as e:
                    logger.error(f"Error migrate photo: {e}")
            user_update = UserUpdate(
                name=user.name,
                birth_date=user.birth_date,
                photo=final_photo_url,
                theme=user.theme,
                show_sub=user.show_sub
            )
            await user_service.update_user(user.id, user_update)
            user.photo = final_photo_url

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
