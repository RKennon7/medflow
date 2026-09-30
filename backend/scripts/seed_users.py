"""
Script to seed database with some initial users
"""

import asyncio
from app.models import User, UserRole
from app.database import AsyncSessionLocal
from app.security import hash_password

async def seed_users():
    async with AsyncSessionLocal() as session:
        session.add_all([
            User(username="admin", hashed_password=hash_password("password123!"), role=UserRole.CLINICAL_ADMIN),
            User(username="technician", hashed_password=hash_password("password123!"), role=UserRole.FIELD_TECHNICIAN),
            User(username="auditor", hashed_password=hash_password("password123!"), role=UserRole.AUDITOR),
        ])
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_users())