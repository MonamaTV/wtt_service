from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv


load_dotenv()

DB_URL = os.getenv('DB')
engine = create_engine(
    DB_URL
)

session_local = sessionmaker(expire_on_commit=False, bind=engine, autoflush=False)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
