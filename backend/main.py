from typing import Annotated
from fastapi import Depends, FastAPI, Query, HTTPException
from config import Settings, get_settings
from db import create_db_and_tables, SessionDep
from models.User import UserDetail, UserSignIn, UserDB, password_hasher, UserInList
from sqlmodel import select

app = FastAPI()
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/info")
async def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
    }

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/users/")
def create_user(user_in: UserSignIn, session: SessionDep) -> UserDetail:
    user_in_db = UserDB(username=user_in.username, email=user_in.email,
                        full_name=user_in.full_name,
                        password=password_hasher(user_in.password))
    session.add(user_in_db)
    session.commit()
    session.refresh(user_in_db)
    return UserDetail(**user_in_db.dict())

@app.get("/users/")
def read_users(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> list[UserInList]:
    _users = session.exec(select(UserDB)
                         .offset(offset)
                         .limit(limit)).all()
    print(_users)
    users = list(map(lambda user: UserInList(**user.dict()), _users))

    return users

@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> UserDetail:
    _user = session.get(UserDB, user_id)
    if not _user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDetail(**_user.dict())