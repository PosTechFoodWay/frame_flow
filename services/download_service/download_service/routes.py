import aioboto3
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from .config import config

router = APIRouter()

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


async def stream_s3_file(bucket: str, key: str, aws_session: aioboto3.Session):
    try:
        async with aws_session.client("s3") as s3_client:
            response = await s3_client.get_object(Bucket=bucket, Key=key)
            stream = response["Body"]

            chunk_size = 1024 * 1024  # 1MB
            while True:
                chunk = await stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to stream file: {e}"
        )


@router.get("/download/{event_id}")
async def upload_file(
    request: Request,
    event_id: str,
    user_id: str = Depends(get_current_user_id),
):
    headers = {"Content-Disposition": "attachment; filename=frames.zip"}
    return StreamingResponse(
        stream_s3_file(
            config.s3_bucket_name, f"{user_id}/{event_id}/frames.zip", request.app.state.aws_session
        ),
        headers=headers,
        media_type="application/zip",
    )


@router.get("/health")
async def health():
    return {"message": "Upload service is running"}
