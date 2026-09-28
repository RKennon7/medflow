from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal

# FastAPI dependency to provide an async db session to any route:
async def get_db() -> AsyncGenerator[AsyncSession | None]:
    async with AsyncSessionLocal as session:
        yield session
        
