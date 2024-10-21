from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    name: str
    surname: str
    email: EmailStr
    telegram_id: int


class UserRegister(User):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(User):
    id: int
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
