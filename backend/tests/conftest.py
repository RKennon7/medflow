"""
shared pytest fixture: isolated test DB, a dependency-overridden FastAPI test client,
and JWT helpers for testing each RBAC role without hitting any real /auth/token endpoints on every test.

"""

import os
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.dependencies import get_db
from app.main import app
from app.models import Base, Hospital, User, UserRole
from app.security import create_access_token, hash_password

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/medflow_test"
)

# separate async engine/session factory just for tests
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

"""
runs once per test that requests it. builds a fresh empty schema before each test runs,
yields a session for the test body to use, then tears it down afterward.
"""
@pytest_asyncio.fixture
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# depends on the db_session and swaps out the real get_db for the test version
@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

# creates one user per rbac role via ORM
@pytest_asyncio.fixture
async def seeded_users(db_session):
    users = {
        "admin": User(username="test_admin", hashed_password=hash_password("pw"), role=UserRole.CLINICAL_ADMIN),
        "technician": User(username="test_technician", hashed_password=hash_password("pw"), role=UserRole.FIELD_TECHNICIAN),
        "auditor": User(username="test_auditor", hashed_password=hash_password("pw"), role=UserRole.AUDITOR),
    }
    for user in users.values():
        db_session.add(user)
    await db_session.commit()
    for user in users.values():
        await db_session.refresh(user)
    return users

# create a test entry in the hospitals table
async def seeded_hospital(db_session):
    hospital = Hospital(name="Test Hospital", location_region="Test Region", capacity=10, supervisor_id=1)
    db_session.add(hospital)
    await db_session.commit()
    await db_session.refresh(hospital)
    return hospital

# build a JWT for seeded user to simulate logged in user for testing
def auth_header(user: User) -> dict[str, str]:
    token = create_access_token(data={"sub": user.username, "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}
        