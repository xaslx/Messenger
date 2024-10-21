from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.chat import Message


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    name: Mapped[str]
    surname: Mapped[str]
    registered_at: Mapped[DateTime] = mapped_column(DateTime)
    telegram_id: Mapped[int]
