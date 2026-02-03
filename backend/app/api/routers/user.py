from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.db import get_db
from app.core.security import (
    verify_jwt_token
)
from app.core.dependencies import get_client_s3, get_current_user_id
from app.services.subscription_service import SubscriptionService
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.block import BlockCreate, UpdateBlock
from app.core.s3_client import S3Client

logger = logging.getLogger(__name__)


router = APIRouter(prefix='/users', tags=['users'])
security = HTTPBearer()


@router.get('/me')
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_for_main_screen(
        user_id=user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )

    return user


@router.post("/user_test_create")
async def create_test_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # telegram_id = 120983122
    # first_name = "KIKOS"
    # last_name = "Admin"
    # username = "Konstitution"
    # photo_url = "saoidasd"

    user_service = UserService(db)
    user = await user_service.get_user_by_telegram_id(user_data.telegram_id)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    try:
        user = await user_service.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Exception as e: {str(e)}"
        )


@router.put("/me")
async def update_current_user(
    user_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    service = UserService(db)
    user = await service.update_user(user_id, user_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/all")
async def get_all_users(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    users = await service.get_all_users(limit)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users not found"
        )
    return users


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    # is_book = await service.check_block_status(
    #     user_id, current_user_id
    # )
    # if not is_book:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Cannot access blocked user"
    #     )
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/block/{blocked_id}")
async def block_user(
    block_data: BlockCreate,
    blocker_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    if blocker_id == block_data.blocked_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block yourself "
        )
    service = UserService(db)
    block = await service.block_user(blocker_id, block_data)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to block user"
        )
    return block


@router.put("/block/{blocked_id}")
async def update_block(
    blocked_id: int,
    update_block: UpdateBlock,
    blocker_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    update = await service.update_block(
        blocked_id=blocked_id,
        blocker_id=blocker_id,
        update_data=update_block
    )
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to block user"
        )
    return update


@router.delete("/block/{blocked_id}")
async def unblock_user(
    blocked_id: int,
    blocker_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    success = await service.unblock_user(blocker_id, blocked_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block record not found"
        )
    return {'message': 'User unblocked successfully'}


@router.get("/block/status/{user_id}")
async def check_block_status(
    blocker_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    is_blocked = await service.check_block_status(blocker_id, user_id)
    return {"is_blocked": is_blocked}


@router.get("/block/list")
async def get_blocked_user_list(
    blocker_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    list_blocked = await service.get_user_block(blocker_id)
    if not list_blocked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No bloked users found"
        )
    return list_blocked
