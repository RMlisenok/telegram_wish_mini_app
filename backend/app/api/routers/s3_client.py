from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from app.core.dependencies import get_client_s3, get_current_user_id

from app.core.s3_client import S3Client


router = APIRouter(prefix='/s3', tags=['s3'])
security = HTTPBearer()


@router.post("/file/")
async def upload_file(
    file: UploadFile,
    user_id: int = Depends(get_current_user_id),
    s3_client: S3Client = Depends(get_client_s3)
):
    try:
        file_url_save = await s3_client.upload_fastapi_file(file)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "File uploaded successfully",
                "filename": file.filename,
                "file_url": file_url_save,
                "content_type": file.content_type,
                "size": file.size
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/file/replace")
async def update_file(
    file_url: str,
    file: UploadFile,
    user_id: int = Depends(get_current_user_id),
    s3_client: S3Client = Depends(get_client_s3)
):
    try:

        file_url_save = await s3_client.update_file(file_url, file)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "File update successfully",
                "filename": file.filename,
                "file_url": file_url_save,
                "content_type": file.content_type,
                "size": file.size
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/file/delete")
async def delete_file(
    file_url: str,
    user_id: int = Depends(get_current_user_id),
    s3_client: S3Client = Depends(get_client_s3)
):
    status_deleted = await s3_client.delete_file(file_url)
    if not status_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "FIle delete successful",
            "file_url": file_url
        }
    )
