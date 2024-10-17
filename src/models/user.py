from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    name: Mapped[str]
    surname: Mapped[str]
    registered_at: Mapped[DateTime] = mapped_column(DateTime)