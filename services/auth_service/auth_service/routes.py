from fastapi import APIRouter, Depends, HTTPException, status

from .models import UserLogin, UserRegister
from .service import AuthService, get_auth_service

router = APIRouter()


@router.post("/register")
async def register_user(
    user_data: UserRegister, auth_service: AuthService = Depends(get_auth_service)
):
    result = await auth_service.register_user(user_data.email, user_data.password)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result


@router.post("/login")
async def login_user(login_data: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    result = await auth_service.login_user(login_data.email, login_data.password)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result["error"])
    return result


@router.get("/validate-token")
async def validate_jwt_token(token: str, auth_service: AuthService = Depends(get_auth_service)):
    result = await auth_service.validate_token(token)
    return result
