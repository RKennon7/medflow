""" 
endpoint routes for user login and registration:

added implementation for Refresh Tokens
"""

import jwt, uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models import User, UserRole, RefreshToken
from app.schemas.user import Token, UserCreate, UserRead, RefreshRequest
from app.security import create_access_token, hash_password, verify_password, create_refresh_token, hash_token, decode_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

# helper to store a new refresh token in the DB:
async def store_refresh_token(
        db: AsyncSession,
        user_id: int,
        token: str,
        chain_id: str,
        issued_at: datetime,
        expires_at: datetime
):
    db.add(RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token),
        chain_id=chain_id,
        issued_at=issued_at,
        expires_at=expires_at,
    ))

# login endpoint: POST
@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    # get username from form data and query db for user:
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    # verify user exists and password matches
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # correct credentials: create JWT and return it
    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    refresh_token, iat, exp = create_refresh_token({"sub": str(user.id)})
    await store_refresh_token(db, user.id, refresh_token, uuid.uuid4().hex, iat, exp)
    await db.commit()
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

# register new user endpoint: requires admin role
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN)),
) -> User:
    # check if user already exists in the db
    existing = await db.execute(select(User).where(func.lower(User.username) == payload.username.lower()))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"username '{payload.username}' is already taken",
        )

    # create user obj from payload
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=payload.role
    )

    # persist user to the db
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# endpoint to refresh the user's login if refresh token is valid
@router.post("/refresh", response_model=Token)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    # print(repr(body.refresh_token), body.refresh_token.count("."))
    # decode the provided refresh token
    try:
        payload = decode_refresh_token(body.refresh_token)
    except jwt.PyJWTError as e:
        # print("DECODE FAILED:", type(e).__name__, e)
        raise HTTPException(401, "Invalid refresh token")

    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_token(body.refresh_token))
        .with_for_update() # serialize concurrent refreshes of same token
    )
    record = result.scalar_one_or_none()

    if record is None or str(record.user_id) != payload["sub"]:
        raise HTTPException(401, "Invalid refresh token")
    
    # kill the user's session if the refresh token was already revoked
    if record.revoked:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.chain_id == record.chain_id)
            .values(revoked=True)
        )
        await db.commit()
        raise HTTPException(401, "Refresh token reuse detected")

    # check if refresh token is expired
    if record.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(401, "Refresh token expired")

    # rotate tokens within same chain
    user = await db.get(User, record.user_id)
    if user is None:
        raise HTTPException(401, "Invalid refresh token")
    record.revoked = True
    new_refresh, iat, exp = create_refresh_token({"sub": str(user.id)})
    await store_refresh_token(db, user.id, new_refresh, record.chain_id, iat, exp)
    await db.commit()
    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    return Token(access_token=access_token, refresh_token=new_refresh, token_type="bearer")

# endpoint for user logout
@router.post("/logout")
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_token(body.refresh_token))
    )
    record = result.scalar_one_or_none()
    if record:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.chain_id == record.chain_id)
            .values(revoked=True)
        )
        await db.commit()
    return {"ok": True}
