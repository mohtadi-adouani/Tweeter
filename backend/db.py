from fastapi.params import Depends
from sqlalchemy import create_engine
from typing import Annotated
from sqlmodel import SQLModel, Session

from config import get_settings

settings = get_settings()

sqlite_file_name = settings.sqlite_file_name
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]