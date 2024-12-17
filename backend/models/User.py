from pydantic import BaseModel, EmailStr
from config import get_settings

from sqlmodel import Field, SQLModel


class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str
    full_name: str
    password: str


class UserDetail(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

class UserInList(BaseModel):
    id: int
    username: str

class UserSignIn(BaseModel):
    username: str
    email: str
    full_name: str
    password: str


def password_hasher(raw_password: str):
    settings = get_settings()
    return settings.password_hash_secret_word + raw_password