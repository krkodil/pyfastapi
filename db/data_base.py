from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://python:password@localhost/python"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)

DatabaseSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DataBaseModel = declarative_base()


# Dependency
def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()
