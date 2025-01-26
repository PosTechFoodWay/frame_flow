# Fábrica para injeção de dependências
import aioboto3
from fastapi import Depends, Request
from redis.asyncio import Redis

from upload_service.repo import FileRepository, get_file_repo

from .upload import UploadService


async def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis_client


async def get_aws_session(request: Request) -> aioboto3.Session:
    return request.app.state.aws_session


async def get_upload_service(
    file_repo: FileRepository = Depends(get_file_repo),
    redis_client: Redis = Depends(get_redis_client),
    aws_session: aioboto3.Session = Depends(get_aws_session),
) -> UploadService:
    return UploadService(file_repo, redis_client, aws_session)


__all__ = ["get_upload_service", "get_redis_client", "UploadService"]
