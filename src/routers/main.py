from datetime import datetime
from fastapi import (
    APIRouter,
    Request,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    BackgroundTasks,
)
from src.models.chat import Message
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.message import MessageCreate, MessageRead
from src.utils.jinja_template import templates
from src.utils.utils import notify_user
from database import get_async_session
from src.auth.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from src.schemas.user import UserOut
from src.repositories.chat import ChatRepository
from logger import logger
from redis_init import redis
from src.tasks.task import send_notify


main_router: APIRouter = APIRouter(tags=["Мессенджер"])

active_connections: dict[int, WebSocket] = {}


@main_router.get("/messages")
async def get_main_page(
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Основная страница где отображается список пользователей."""

    all_users: list[UserOut] = await UserRepository.find_all(session=session)

    return templates.TemplateResponse(
        request=request, name="base.html", context={"user": user, "people": all_users}
    )


@main_router.get("/me")
async def get_myprofile_template(
    request: Request, user: Annotated[User, Depends(get_current_user)]
):
    """Страница для отображения профиля"""

    return templates.TemplateResponse(
        request=request, name="me.html", context={"user": user}
    )


@main_router.get("/messages/{user_id}")
async def get_dialog_by_id(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(get_current_user)],
):

    if user:

        # получаем список сообщений между 2мя пользователями
        dialog: Message = await ChatRepository.get_messages_between_users(
            user_id_1=user_id, user_id_2=user.id, session=session
        )

        # получаем собеседника
        partner: User = await UserRepository.find_one_or_none(
            session=session, id=user_id
        )

        # сериализуем в модель pydantic
        from_orm: MessageRead = [
            MessageRead.model_validate(i) if dialog else None for i in dialog
        ]

        # проверка, в сети ли собеседник
        is_online = await redis.get(f"user:{partner.id}:is_online")
        return {
            "user": {"id": user.id, "name": user.name, "surname": user.surname},
            "partner": {
                "id": partner.id,
                "name": partner.name,
                "surname": partner.surname,
                "is_online": True if is_online else False,
            },
            "messages": [
                {
                    "senderId": message.sender_id,
                    "senderName": (
                        partner.name if message.sender_id == partner.id else user.name
                    ),
                    "text": message.content,
                    "timestamp": message.date_time.strftime("%d.%m.%Y %H:%M"),
                }
                for message in from_orm
            ],
        }


@main_router.post("/messages")
async def send_message(
    message: MessageCreate,
    bg_task: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(get_current_user)],
):

    current_date: datetime = datetime.now()

    # добавляем новое сообщение в диалог между 2мя пользователями
    await ChatRepository.add(
        session=session,
        sender_id=user.id,
        content=message.content,
        recipient_id=message.recipient_id,
        date_time=current_date,
    )

    # сообщение от собеседника
    message_data: dict[str, User | MessageCreate] = {
        "sender_id": user.id,
        "recipient_id": message.recipient_id,
        "content": message.content,
        "timestamp": current_date.strftime("%d.%m.%Y %H:%M"),
        "sender_name": user.name,
    }

    # отправляем сообщение через websocket
    await notify_user(
        user_id=user.id, message=message_data, active_connections=active_connections
    )

    # проверка, в сети ли собеседник
    partner = await redis.get(f"user:{message.recipient_id}:is_online")
    if not partner:

        # если собеседник не онлайн, то делаем ему уведомление о новом сообщении, через Телеграм
        partner: int = await UserRepository.find_one_or_none(
            session=session, id=message.recipient_id
        )
        bg_task.add_task(send_notify, user_id=partner.telegram_id)

    return message_data


@main_router.websocket("/ws/messages/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # websocket соединение
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Получено сообщение от пользователя: {user_id}: {data}")
    except WebSocketDisconnect as e:
        logger.error(f"Ошибка в соединении для пользователя: {user_id}: {str(e)}")
    finally:
        active_connections.pop(user_id, None)
        logger.info(f"Пользователь: {user_id} отключился")
