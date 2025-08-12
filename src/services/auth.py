from datetime import datetime, timezone, timedelta

from fastapi import Response, HTTPException
from sqlalchemy.exc import NoResultFound
from passlib.context import CryptContext
import jwt

from src.schemas.users import UserAdd, UserRequestAdd
from src.services.base import BaseService
from src.config import settings


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def register_user(self, data: UserRequestAdd):
        users = await self.db.users.get_all()
        emails = [user.email for user in users]
        if data.email in emails:
            raise HTTPException(status_code=409, detail="User with this email already exists")

        hashed_password = AuthService().hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)

        await self.db.users.add(new_user_data)
        await self.db.session.commit()

    async def login_user(self, data: UserRequestAdd, response: Response):
        try:
            user = await self.db.users.get_user_with_hashed_password(email=data.email)
        except NoResultFound:
            raise HTTPException(status_code=401, detail="User with this email not found")

        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password")

        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)

        return access_token
    
    async def get_me(self, user_id: int):
        return await self.db.users.get_one(id=user_id)

    async def logout_user(self, response: Response):
        response.delete_cookie("access_token")
