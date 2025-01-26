from fastapi import Depends

from auth_service.repo import UserRepository, get_user_repository

from .auth import AuthService


async def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    """
    Função de fábrica que cria e retorna uma instância de AuthService,
    injetando automaticamente o UserRepository (que recebe a conexão asyncpg).
    """
    return AuthService(user_repo)


__all__ = ["get_auth_service", "AuthService"]
