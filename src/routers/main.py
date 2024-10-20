from datetime import datetime
from fastapi import APIRouter, Request, Depends, WebSocket, WebSocketDisconnect
from src.models.chat import Message
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.message import MessageCreate, MessageRead
from src.utils.jinja_template import templates
from database import get_async_session
from src.auth.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from src.schemas.user import UserOut
from src.repositories.chat import ChatRepository
from logger import logger
from redis_init import redis



main_router: APIRouter = APIRouter(
    tags=['Мессенджер']
)

active_connections: dict[int, WebSocket] = {}





@main_router.get('/messages')
async def get_main_page(
    request: Request, 
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)]):

    all_users: list[UserOut] = await UserRepository.find_all(session=session)
  
    return templates.TemplateResponse(
        request=request,
        name='base.html',
        context={'user': user, 'people': all_users}
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



@main_router.get('/messages/{user_id}')
async def get_dialog_by_id(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(get_current_user)]
):

    if user:
        
        res: Message = await ChatRepository.get_messages_between_users(user_id_1=user_id, user_id_2=user.id, session=session)
        user_2: User = await UserRepository.find_one_or_none(session=session, id=user_id)


        from_orm: MessageRead = [MessageRead.model_validate(i) if res else None for i in res]
        is_online = await redis.get(f'user:{user_2.id}:is_online')
        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "surname": user.surname
            },
            "partner": {
                "id": user_2.id,
                "name": user_2.name,
                "surname": user_2.surname,
                "is_online": True if is_online else False
            },
            "messages": [{
                "senderId": message.sender_id,
                "senderName": user_2.name if message.sender_id == user_2.id else user.name,
                "text": message.content,
                "timestamp": message.date_time.strftime('%d.%m.%Y %H:%M')
            } for message in from_orm]
        }

        


    
@main_router.post('/messages')
async def send_message(
    message: MessageCreate, 
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(get_current_user)]):
  
    current_date = datetime.now()
    await ChatRepository.add(
        session=session,
        sender_id=user.id,
        content=message.content,
        recipient_id=message.recipient_id,
        date_time=current_date
    )
    message_data: dict[str, User | MessageCreate] = {
        'sender_id': user.id,
        'recipient_id': message.recipient_id,
        'content': message.content,
        'timestamp': current_date.strftime('%d.%m.%Y %H:%M'),
        'sender_name': user.name
    }

    await notify_user(user.id, message_data)
    # await notify_user(message.recipient_id, message_data)  #
        
    return message_data


async def notify_user(user_id: int, message: dict):
    if user_id in active_connections:
        websocket = active_connections[user_id]
        try:
            await websocket.send_json(message)
            logger.info(f'Сообщение отправлено пользователю {user_id}: сообщение - {message}')
        except Exception as e:
            logger.error(f'Ошибка отправки сообщения пользователю: {user_id}: {str(e)}')
    else:
        logger.warning(f'Пользователь: {user_id} не подключен')




@main_router.websocket('/ws/messages/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f'Получено сообщение от пользователя: {user_id}: {data}')
    except WebSocketDisconnect as e:
        logger.error(f'Ошибка в соединении для пользователя: {user_id}: {str(e)}')
    finally:
        active_connections.pop(user_id, None)
        logger.info(f'Пользователь: {user_id} отключился')
