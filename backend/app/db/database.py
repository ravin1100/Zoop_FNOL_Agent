from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Async SQLite URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./fnol.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL, echo=True, future=True  # Set to False in production
)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


# Dependency for getting db session in FastAPI or other apps
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
