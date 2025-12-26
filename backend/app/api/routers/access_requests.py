from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.access_request import AccessRequest
from app.services.access_request_service import AccessRequestService
from app.schemas.access_request import (
    AccessRequestCreate,
    AccessRequestResponse,
    AccessRequestsResponse,
    AccessRequestWithDetails,
    UpdateAccessRequest
)

router = APIRouter(prefix="access-requests", tags=["access-requests"])
