from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")

# SQLAlchemy database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal class to create a session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
