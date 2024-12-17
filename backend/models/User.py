from pydantic import BaseModel, EmailStr

from main import get_settings


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    pass

class UserInDB(UserBase):
    hashed_password: str


def password_hasher(raw_password: str):
    settings = get_settings()
    return settings.password_hash_secret_word + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db
