from datetime import datetime, timedelta, timezone
from app.config import settings
import jwt
import bcrypt
import hashlib, uuid

"""
Add password hashing, pw verification, JWT creation and JWT decoding
"""
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

# Using bcrypt to hash and verify password
def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# create JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# decode JWT
def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Not an access token")
    return payload

"""
TODO: functions to create refresh token, hash refresh token,
"""
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

# create Refresh Token:
def create_refresh_token(data: dict) -> tuple[str, datetime, datetime]:
    """returns  (token, issued_at, expires_at) for the caller to store"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "refresh",
        "jti": uuid.uuid4().hex,
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM), now, expire

# decode refresh token
def decode_refresh_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token")
    return payload
