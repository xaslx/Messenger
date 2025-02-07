from sqlalchemy import delete, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from logger import logger
from src.repositories.base import AbstractRepository


class SQLAlchemyRepository(AbstractRepository):

    model = None

    @classmethod
    async def add(
        self,
        session: AsyncSession,
        **data: dict,
    ):
        try:
            stmt = (
                insert(self.model)
                .values(**data)
                .returning(self.model.__table__.columns)
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.mappings().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            logger.error(
                "Ошибка при добавлении записи в базу данных",
                extra={"данные": data, "ошибка": e},
            )

    @classmethod
    async def find_one_or_none(
        self,
        session: AsyncSession,
        **filter_by,
    ):
        try:
            stmt = select(self.model).filter_by(**filter_by)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as e:
            logger.error(
                f"Ошибка при поиске значения в базе данных", extra={"ошибка": e}
            )

    @classmethod
    async def find_all(self, session: AsyncSession, **filter_by):
        try:
            stmt = select(self.model).filter_by(**filter_by)
            res = await session.execute(stmt)
            return res.scalars().all()
        except (SQLAlchemyError, Exception) as e:
            logger.error(
                f"Ошибка при поиске всех значений в базе данных", extra={"ошибка": e}
            )
