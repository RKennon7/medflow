from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, require_role
from app.models import User, UserRole
from app.schemas.health import HealthDetails, CheckResult
import asyncio
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

router = APIRouter(prefix="/health", tags=["health"])

# simple health check endpoint
@router.get("/health")
async def health_check() -> dict[str,str]:
    return{"status": "ok"}

# health check endpoint to check if database is available/ready
@router.get("/health/ready")
async def health_check_db_ready(
    db: AsyncSession = Depends(get_db)
):
    try:
        await asyncio.wait_for(db.execute(text("SELECT 1")), timeout=3)

    except (SQLAlchemyError, OSError, asyncio.TimeoutError):
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "offline"}
        )
    return{"status": "ok", "database": "online"}

# helper to check database for detail
async def check_db(db: AsyncSession) -> CheckResult:
    try:
        version = await asyncio.wait_for(db.scalar(text("SELECT version()")), timeout=3)
        return CheckResult(status="ok", version=version)
    except (SQLAlchemyError, OSError, asyncio.TimeoutError) as e:
        return CheckResult(status="unavailable", error=type(e).__name__)

# helper to check s3 for detail
async def check_s3() -> CheckResult:
    s3_client = boto3.client(
        's3',
        config=Config(
        connect_timeout=3,
        read_timeout=3,
        retries={"max_attempts": 1},
        ),
    )
    try:
        resp = s3_client.head_bucket(
            Bucket="medflow-frontend-rbk7",
        )
        fields = {
            "status": "ok",
            "bucket": resp.get("BucketArn"),
            "region": resp.get("BucketRegion"),
        }
    except ClientError as e:
        fields = {"status": "unavailable", "error": e.response["Error"]["Code"]}

    result = CheckResult(**fields)
    return result


# admin-only health check reports DB and S3 status separately
@router.get("/health/detail", response_model=HealthDetails, response_model_exclude_none=True, )
async def health_check_detail(
    response: Response,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN))
):
    database, s3 = await asyncio.gather(check_db(db), check_s3())
    healthy = database.status == 'ok' and s3.status == 'ok'
    if not healthy:
        # something is down, give 503
        response.status_code = 503
    return HealthDetails(status="ok" if healthy else "degraded", database=database, s3=s3)