from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from src.models.chat import Message

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    name: Mapped[str]
    surname: Mapped[str]
    registered_at: Mapped[DateTime] = mapped_column(DateTime)
    telegraim_id: Mapped[int]

    sent_messages: Mapped[list['Message']] = relationship(
        'Message', 
        foreign_keys='Message.sender_id', 
        back_populates='sender', 
        cascade='all, delete-orphan')
    received_messages: Mapped[list['Message']] = relationship(
        'Message', 
        foreign_keys='Message.recipient_id', 
        back_populates='recipient', 
        cascade='all, delete-orphan')