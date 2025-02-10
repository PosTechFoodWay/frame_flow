from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from upload_service.config import config
from upload_service.service import UploadService, get_upload_service

router = APIRouter()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}
AUTH_VALIDATE_ENDPOINT = "/auth/validate-token"


async def get_current_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = auth_header.split(" ")[1]

    url = f"{config.auth_service_url}{AUTH_VALIDATE_ENDPOINT}"
    params = {"token": token}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        # If the auth_service returns non-200, treat as invalid
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to validate token with auth_service",
            )
        data = response.json()

    if not data.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    payload = data.get("payload", {})
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload missing 'sub'"
        )

    return user_id


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    upload_svc: UploadService = Depends(get_upload_service),
):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            file_size = int(content_length)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large. Maximum size is 100 MB.",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content-length header."
            )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{file_ext}'. Allowed: {ALLOWED_EXTENSIONS}.",
        )

    result = await upload_svc.upload_file_to_s3(file, user_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result


@router.get("/upload/status/{event_id}")
async def upload_status(event_id: str, upload_svc: UploadService = Depends(get_upload_service)):
    status = await upload_svc.get_upload_status(event_id)
    return {"status": status}
