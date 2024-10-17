from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    name: str
    surname: str
    email: EmailStr
    registered_at: datetime


class UserIn(User):
    password: str


class UserOut(User):
    id: int