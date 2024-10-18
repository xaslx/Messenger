import uuid
from fastapi import APIRouter, HTTPException, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from src.models.user import User
from src.utils.jinja_template import templates
from database import get_async_session
from src.auth.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from src.schemas.user import UserOut
from redis_init import redis


async def create_session(user_id: str):
    session_id = str(uuid.uuid4())  # Генерация уникального идентификатора сессии
    await redis.set(session_id, user_id)  # Сохранение сессии в Redis
    return session_id

# Функция для получения сессии
async def get_session(session_id: str):
    user_id = await redis.get(session_id)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return user_id

# Функция для удаления сессии
async def delete_session(session_id: str):
    await redis.delete(session_id)



main_router: APIRouter = APIRouter(
    tags=['Мессенджер']
)


people = [
    UserOut(name='Maksim', surname='Ivanov', email='gregrger@gmail.com', id=1),
    UserOut(name='Maksim', surname='Ivanov', email='gregrger@gmail.com', id=2),
    UserOut(name='Maksim', surname='Ivanov', email='gregrger@gmail.com', id=3),
    UserOut(name='Maksim', surname='Ivanov', email='gregrger@gmail.com', id=4),
    UserOut(name='Maksim', surname='Ivanov', email='gregrger@gmail.com', id=5),
    UserOut(name='Maksim', surname='Ivanov', email='gregrger@gmail.com', id=6),
    UserOut(name='Maksim', surname='Ivanov', email='gregrger@gmail.com', id=7),
    UserOut(name='Maksim', surname='Ivanov', email='gregrger@gmail.com', id=8),
]

@main_router.get('/')
async def get_main_page(
    request: Request, 
    user: Annotated[User, Depends(get_current_user)]):

    return templates.TemplateResponse(
        request=request,
        name='base.html',
        context={'user': user, 'people': people}
    )


@main_router.get('/me')
async def get_myprofile_template(
    request: Request,
    user: Annotated[User, Depends(get_current_user)]
):
    return templates.TemplateResponse(
        request=request,
        name='me.html',
        context={'user': user}
    )



@main_router.get('/dialogs/{dialog_id}')
async def get_dialog_by_id(
    request: Request, 
    dialog_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user)
):
    s = 5
    if dialog_id == s:

        return {
        "user": {
            "id": 2,
            "name": "Иван",
            "surname": "Иванов"
        },
        "messages": [
            {
                "senderName": "Иван",
                "text": "Привет! Как дела?"
            },
            {
                "senderName": "Вы",
                "text": "Привет, Иван! Все хорошо, а у тебя?"
            },
            {
                "senderName": "Иван",
                "text": "Тоже хорошо, спасибо!"
            }
        ]
    }
    return {'Диалога еще нет'}

    
