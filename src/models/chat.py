from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime
from typing import TYPE_CHECKING


if TYPE_CHECKING:
   from src.models.user import User

class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    recipient_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    content: Mapped[str] = mapped_column(String(1000))
    date_time: Mapped[datetime] = mapped_column(DateTime)