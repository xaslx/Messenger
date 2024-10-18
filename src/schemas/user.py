from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class User(BaseModel):
    name: str
    surname: str
    email: EmailStr



class UserRegister(User):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(User):
    id: int
    
    
    model_config = ConfigDict(from_attributes=True)

    