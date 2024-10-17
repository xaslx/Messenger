from src.repositories.base import AbstractRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, delete, select
from logger import logger
from sqlalchemy.exc import SQLAlchemyError



class SQLAlchemyRepository(AbstractRepository):

    model = None

    def __init__(self, session: AsyncSession):
        self.session = session
 

    async def add(self, **data: dict):
        try:
            stmt = insert(self.model).values(**data).returning(self.model.__table__.columns)
            res = await self.session.execute(stmt)
            await self.session.commit()
            return res.mappings().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            logger.error(
                'Ошибка при добавлении записи в базу данных', extra={'данные': data, 'ошибка': e}
            )


    async def find_one_or_none(self, **filter_by):
        try:
            stmt = select(self.model).filter_by(**filter_by)
            res = await self.session.execute(stmt)
            return res.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as e:
            logger.error(f'Ошибка при поиске значения в базе данных', extra={'ошибка': e})


    async def find_all(self, **filter_by):
        try:
            stmt = select(self.model).filter_by(**filter_by)
            res = await self.session.execute(stmt)
            return res.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as e:
            logger.error(f'Ошибка при поиске всех значений в базе данных', extra={'ошибка': e})

    async def delete(self, id: int) -> int:
        try:
            stmt = delete(self.model).filter_by(id=id).returning(self.model.id)
            await self.session.execute(stmt)
            await self.session.commit()
        except (SQLAlchemyError, Exception) as e:
            logger.error(f'Ошибка при удалении значения из базы данных', extra={'ошибка': e})