from fastapi import APIRouter, Response

from src.schemas.users import UserRequestAdd
from src.services.auth import AuthService
from src.CRUD.dependencies import UserIdDep, DBDep


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(db: DBDep, data: UserRequestAdd) -> dict:
    await AuthService(db).register_user(data)
    return {"status": "ok"}


@router.post("/login")
async def login_user(db: DBDep, data: UserRequestAdd, response: Response) -> dict:
    access_token = await AuthService(db).login_user(data, response)
    return {"access_token": access_token}


@router.get("/me")
async def get_me(user_id: UserIdDep, db: DBDep):
    return await AuthService(db).get_me(user_id)


@router.post("/logout")
async def logout_user(response: Response):
    await AuthService().logout_user(response)
    return {"status": "ok"}
