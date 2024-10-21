from logger import logger


async def notify_user(user_id: int, message: dict, active_connections: dict):
    #отправка сообщения через Websocket
    if user_id in active_connections:
        websocket = active_connections[user_id]
        try:
            await websocket.send_json(message)
            logger.info(f'Сообщение отправлено пользователю {user_id}: сообщение - {message}')
        except Exception as e:
            logger.error(f'Ошибка отправки сообщения пользователю: {user_id}: {str(e)}')
    else:
        logger.warning(f'Пользователь: {user_id} не подключен')