from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


class CrudRepository:
    def __init__(self, session, model):
        self.session = session
        self.model = model


    async def get_all_by(self, **filter_by):
            stmt = select(self.model).filter_by(**dict(filter_by))
            result = await self.session.execute(stmt)
            result =  result.scalars().all()
            return result


    async def get_one_by(self, **filter_by):
        try:
            stmt = select(self.model).filter_by(**dict(filter_by))
            result = await self.session.execute(stmt)
            result = result.scalars().first()
            return result
        except SQLAlchemyError as e:
            return None


    async def create_one(self, data: dict):
            new_data = self.model(**data)
            self.session.add(new_data)
            await self.session.commit()
            await self.session.refresh(new_data)
            return new_data


    async def get_all(self):
            stmt = select(self.model)
            result = await self.session.execute(stmt)
            result = result.scalars().all()
            return result


