from pydantic import BaseModel, EmailStr, ConfigDict


class UserRequestAdd(BaseModel):
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str


class User(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UsersWithHashedPassword(User):
    hashed_password: str
