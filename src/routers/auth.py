from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import get_current_user
from src.auth.auth import get_password_hash, create_access_token, authenticate_user

from database import get_async_session
from exceptions import UserAlreadyExistsException, UserNotFound
from src.models.user import User
from src.utils.jinja_template import templates
from src.repositories.user import UserRepository
from src.schemas.user import UserLogin, UserRegister, UserOut


auth_router: APIRouter = APIRouter(
    prefix="/auth", tags=["Аутентификация и Авторизация"]
)


@auth_router.get("/register", status_code=200)
async def get_register_template(
    request: Request, user: Annotated[UserOut, Depends(get_current_user)]
) -> HTMLResponse:
    """Страница с регистрацией"""

    return templates.TemplateResponse(
        "register.html",
        {"request": request, "user": user},
    )


@auth_router.post("/register", status_code=201)
async def rigister_user(
    user: UserRegister,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserOut:
    """Регистрация нового пользователя"""

    exist_user: UserOut = await UserRepository.find_one_or_none(
        session=session, email=user.email
    )

    if exist_user:
        raise UserAlreadyExistsException
    current_date_time: datetime = datetime.utcnow()
    hashed_password: str = get_password_hash(user.password)
    new_user: UserOut = await UserRepository.add(
        session=session,
        **user.model_dump(exclude="password"),
        hashed_password=hashed_password,
        registered_at=current_date_time,
    )
    return new_user


@auth_router.post("/login", status_code=200)
async def login_user(
    response: Response,
    user: UserLogin,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> str:
    """Вход пользователя"""

    user: UserOut = await authenticate_user(user.email, user.password, async_db=session)
    if not user:
        raise UserNotFound

    access_token, expire = create_access_token({"sub": str(user.id)})
    max_age = (expire - datetime.utcnow()).total_seconds()

    response.set_cookie(
        "user_access_token", access_token, httponly=True, max_age=max_age
    )
    return access_token


@auth_router.get("/after_register", status_code=200)
async def get_after_register_template(
    request: Request, user: Annotated[User, Depends(get_current_user)]
):
    """Страница после регистрации"""

    return templates.TemplateResponse(
        request=request, name="after_register.html", context={"user": user}
    )


@auth_router.get("/login", status_code=200)
async def get_login_template(
    request: Request, user: Annotated[UserOut, Depends(get_current_user)]
) -> HTMLResponse:
    """Страница со входом"""

    return templates.TemplateResponse(
        request=request, name="login.html", context={"user": user}
    )


@auth_router.post("/logout", status_code=200)
async def logout_user(
    response: Response,
    request: Request,
):
    """Удаление куки"""

    cookies: str | None = request.cookies.get("user_access_token")
    if cookies:
        response.delete_cookie(key="user_access_token")
