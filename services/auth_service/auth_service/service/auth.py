# app/service/auth_service.py

from datetime import datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from auth_service.config import config as app_env_config
from auth_service.repo import UserRepository

SECRET_KEY = app_env_config.auth_key
ALGORITHM = app_env_config.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = app_env_config.access_token_expire_minutes


class AuthService:
    def __init__(self, user_repo: UserRepository):
        """
        O repositório de usuários (user_repo) já está pronto para uso,
        recebendo a conexão 'asyncpg.Connection' da dependência do FastAPI.
        """
        self.user_repo = user_repo

    async def register_user(self, email: str, password: str) -> dict[str, str]:
        """
        Registra um novo usuário caso o e-mail ainda não exista.
        Retorna um dicionário contendo sucesso ou erro.
        """
        # Verifica se já existe
        if await self.user_repo.user_exists(email):
            return {"error": "User already exists"}

        # Hash da senha com bcrypt
        hashed_pwd = self._hash_password(password)

        # Cria o usuário no banco e obtém o UUID gerado
        user_id = await self.user_repo.create_user(email, hashed_pwd)

        return {"msg": "User registered", "user_id": str(user_id)}

    async def login_user(self, email: str, password: str) -> dict[str, str]:
        """
        Faz login, validando e-mail e senha.
        Se válido, gera e retorna o token JWT.
        """
        record = await self.user_repo.get_user_by_email(email)
        if not record:
            return {"error": "Invalid credentials"}

        # Verifica se a senha confere
        stored_hash = record["password_hash"]
        if not self._verify_password(password, stored_hash):
            return {"error": "Invalid credentials"}

        # Gera o token
        token = self._create_access_token({"sub": str(record["id"])})
        return {"access_token": token, "token_type": "bearer"}

    async def validate_token(self, token: str) -> dict[str, Any]:
        """
        Valida o token JWT e retorna {"valid": bool, "payload": dict}.
        Caso inválido, "valid" = False.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return {"valid": True, "payload": payload}
        except JWTError:
            return {"valid": False, "payload": {}}

    # Métodos internos:

    def _hash_password(self, password: str) -> str:
        """
        Gera hash para a senha usando bcrypt.
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode()

    def _verify_password(self, password: str, hashed_pwd: str) -> bool:
        """
        Verifica se a senha em texto puro confere com o hash armazenado.
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_pwd.encode("utf-8"))

    def _create_access_token(self, data: dict) -> str:
        """
        Cria um token JWT com prazo de expiração definido em ACCESS_TOKEN_EXPIRE_MINUTES.
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
