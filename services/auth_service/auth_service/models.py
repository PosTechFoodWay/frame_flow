from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StrictModel(BaseModel):
    """This model don't allow any extra fields"""

    model_config = ConfigDict(extra="forbid")


class UserRegister(StrictModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=20)


class UserLogin(StrictModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=20)


class TokenData(StrictModel):
    access_token: str
    token_type: str = "bearer"
