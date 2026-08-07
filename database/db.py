from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
import os

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

class Base(DeclarativeBase):
    pass


sync_engine = create_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
    pool_size=5,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(sync_engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()