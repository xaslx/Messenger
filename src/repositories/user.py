from src.models.user import User
from src.repositories.sqlalchemy import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model: User = User
