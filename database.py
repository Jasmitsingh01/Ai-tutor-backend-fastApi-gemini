from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy.orm import configure_mappers


from dotenv import load_dotenv

load_dotenv()


# Getting ENV Values from .env file
DATABASE_URL = os.getenv("DATABASE_URL")
configure_mappers()
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fuction For Get Session DATABase 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()