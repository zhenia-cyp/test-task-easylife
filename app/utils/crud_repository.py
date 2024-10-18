import logging
from typing import Union
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)


class CrudRepository:
    """A class for performing asynchronous CRUD operations"""
    def __init__(self, session, model):
        """initializes the class with a session and a model"""
        self.session = session
        self.model = model
        self.logger = logging.getLogger(__name__)


    async def get_all_by(self, **filter_by):
        """this method returns all records matching the given filter conditions"""
        stmt = select(self.model).filter_by(**dict(filter_by))
        result = await self.session.execute(stmt)
        result =  result.scalars().all()
        return result


    async def get_one_by(self, **filter_by):
        """this method returns all records matching the given filter conditions
        or None"""
        try:
            stmt = select(self.model).filter_by(**dict(filter_by))
            result = await self.session.execute(stmt)
            result = result.scalars().first()
            return result
        except SQLAlchemyError as e:
            self.logger.error(" %s", str(e))
            return None


    async def create_one(self, data: dict):
        """this method creates a new record in the database with the given data"""
        new_data = self.model(**data)
        self.session.add(new_data)
        await self.session.commit()
        await self.session.refresh(new_data)
        return new_data


    async def get_all(self):
        """this method returns all records from the database"""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        result = result.scalars().all()
        return result


    async def delete_one(self, delete_param: Union[int, object]):
        """his method deletes a record from the database, either by ID or object """
        if isinstance(delete_param, int):
            stmt = delete(self.model).where(self.model.id == delete_param)
            await self.session.execute(stmt)
        elif isinstance(delete_param, self.model):
            await self.session.delete(delete_param)
        await self.session.commit()
        return True
