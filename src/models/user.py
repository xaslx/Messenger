from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base




class User(Base):
    __tablename__ = "users2"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    name: Mapped[str]
    surname: Mapped[str]
    registered_at: Mapped[DateTime] = mapped_column(DateTime)
    telegram_id: Mapped[int]
