from pydantic import EmailStr
from sqlalchemy import insert, select
from sqlalchemy.exc import NoResultFound

from src.schemas.users import User, UserAdd, UsersWithHashedPassword
from src.models.users import UsersOrm


class UsersRepository:
    model = UsersOrm
    schema = User

    def __init__(self, session):
        self.session = session

    async def add(self, data: UserAdd):
        add_data_stmt = (
            insert(self.model).values(**data.model_dump()).returning(self.model)
        )
        await self.session.execute(add_data_stmt)

    async def get_all(self):
        query = select(self.model)
        result = await self.session.execute(query)
        models = [
            self.schema.model_validate(one, from_attributes=True)
            for one in result.scalars().all()
        ]

        return models
    
    async def get_one(self, **filter: dict):
        query = select(self.model).filter_by(**filter)
        result = await self.session.execute(query)
        model = result.scalar_one()
    
        if model is None:
            return None
        return self.schema.model_validate(model, from_attributes=True)

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise NoResultFound(f"User with email {email} not found")

        return UsersWithHashedPassword.model_validate(model, from_attributes=True)
