from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.access_request import AccessRequest, AccessRequestStatus
from app.services.access_request_service import AccessRequestService
from app.schemas.access_request import (
    AccessRequestCreate,
    AccessRequestResponse,
    AccessRequestsResponse,
    AccessRequestWithDetails,
    UpdateAccessRequest
)

router = APIRouter(prefix="access-requests", tags=["access-requests"])


@router.post("/",
             response_model=AccessRequestWithDetails,
             status_code=status.HTTP_201_CREATED)
async def create_access_request(
    request_data: AccessRequestCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = AccessRequestService(db)
    try:
        result = await service.create_request(user_id, request_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot create request"
        )


@router.get("/{request_id}",
            response_model=AccessRequestWithDetails):
async def get_access_request(
    request_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = AccessRequestService(db)
    try:
        result = await service.get_request(request_id, user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.patch("/{request_id}", response_model=AccessRequestWithDetails)
async def update_access_request(
    request_id: int,
    update_data: UpdateAccessRequest,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = AccessRequestService(db)
    try:
        result = await service.update_request_status(
            request_id,
            update_data,
            user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{request_id}")
async def delete_access_request(
    request_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = AccessRequestService(db)
    try:
        success = await service.delete_request(
            request_id,
            user_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        return {"message": "Request deleted"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/my/requests",
            response_model=AccessRequestResponse)
async def get_my_access_requests(
    user_id: int,
    status_req: Optional[AccessRequestStatus] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = AccessRequestService(db)
    try:
        return await service.get_my_requests(
            user_id,
            status_req,
            limit
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot get request"
        )


@router.get("/my/wishlists",
            response_model=AccessRequestsResponse)
async def get_requests_for_my_wishlists(
    user_id: int,
    status_req: Optional[AccessRequestStatus] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = AccessRequestService(db)
    try:
        return await service.get_requsts_for_my_wishlists(
            user_id,
            status_req,
            limit
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot get request"
        )    
