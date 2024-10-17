from src.repositories.sqlalchemy import SQLAlchemyRepository
from src.models.chat import Message


class ChatRepository(SQLAlchemyRepository):
    model: Message = Message