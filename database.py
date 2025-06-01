from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, JSON
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read PostgreSQL credentials from .env
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
print("Done!", POSTGRES_HOST)
# SQLite Database URL
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create an Async Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Session Local
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()

# Define the model
class CoachData(Base):
    __tablename__ = "coach_data"

    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, index=True)
    exercise_id = Column(Integer, index=True)
    name = Column(String, index=True)
    json_data = Column(JSON)

# Function to create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
