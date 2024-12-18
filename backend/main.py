from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, Query, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from auth.jwt import Token, authenticate_user, get_current_active_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
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
    users = list(map(lambda user: UserInList(**user.dict()), _users))

    return users

@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> UserDetail:
    _user = session.get(UserDB, user_id)
    if not _user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDetail(**_user.dict())

@app.post("/token")
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UserDetail)
async def read_users_me(
    session: SessionDep,
    current_user: Annotated[UserDetail, Depends(get_current_active_user)],
):
    return current_user