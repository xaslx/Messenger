from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User

from src.repositories.user import UserRepository

from config import settings
from database import get_async_session
from exceptions import (
    IncorrectTokenException,
    UserIsNotPresentException,
)
from redis_init import redis
from src.schemas.user import UserOut


def get_token(request: Request):
    token: str = request.cookies.get("user_access_token")
    if not token:
        return None
    return token


def valid_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.SECRET_ALGORITHM)
    except ExpiredSignatureError:
        return None
    except JWTError:
        raise IncorrectTokenException
    return payload


async def get_current_user(
    async_db: AsyncSession = Depends(get_async_session),
    token: str = Depends(get_token),
) -> User:
    if not token:
        return None
    payload = valid_token(token=token)
    user_id: str = payload.get("sub")
    user_data: None | str = await redis.get(f"user:{user_id}")
    if user_data:
        user: UserOut = UserOut.model_validate_json(user_data)
    else:
        user: User = await UserRepository.find_one_or_none(
            id=int(user_id), session=async_db
        )
        if user is None:
            return None
        user_out: UserOut = UserOut.model_validate(user)
        await redis.set(f"user:{user_id}", user_out.model_dump_json(), ex=600)

    if not user_id:
        raise UserIsNotPresentException
    if not user:
        return None
    return user
