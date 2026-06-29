import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from typing import AsyncGenerator


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in your .env file")



engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
    
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit = False,#YOU decide when to commitm, db.commit() 
    autoflush=False,#
    expire_on_commit=False #after commit, keep the object's data
   #   in memory so you can still return it in the response
    
)

class Base(DeclarativeBase):
    pass #its empty, but base inheritted declarative
#this is the modern way

async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()      # commit if everything went fine
        except Exception:
            await session.rollback()    # undo everything if anything failed
            raise                       # re-raise so FastAPI returns the error
        
#later replacable with allembic       
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)