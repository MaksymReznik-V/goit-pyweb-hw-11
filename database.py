import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

Base = declarative_base()

def get_db():
    """
    Provide a database session for FastAPI dependencies.

    Creates a new SQLAlchemy session for each request and guarantees
    that the session is closed after the request has been processed.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
