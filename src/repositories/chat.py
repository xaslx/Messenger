from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.chat import Message
from src.repositories.sqlalchemy import SQLAlchemyRepository


class ChatRepository(SQLAlchemyRepository):
    model: Message = Message

    @classmethod
    async def get_messages_between_users(
        cls, user_id_1: int, user_id_2: int, session: AsyncSession
    ):
        query = (
            select(cls.model)
            .filter(
                or_(
                    and_(
                        cls.model.sender_id == user_id_1,
                        cls.model.recipient_id == user_id_2,
                    ),
                    and_(
                        cls.model.sender_id == user_id_2,
                        cls.model.recipient_id == user_id_1,
                    ),
                )
            )
            .order_by(cls.model.id)
        )
        result = await session.execute(query)
        return result.scalars().all()
