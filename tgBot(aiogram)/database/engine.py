import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


engine = create_async_engine(os.getenv('DATABASE_URL'), echo=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
