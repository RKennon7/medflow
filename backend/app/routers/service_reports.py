import uuid, boto3
from app.config import settings
from app.dependencies import get_db, get_current_user, require_role
from app.models import User, UserRole, ServiceReport
from app.schemas.service_report import ServiceReportCreate, ServiceReportRead
from fastapi import APIRouter, Depends, File, Form, UploadFile, Query
from fastapi.concurrency import run_in_threadpool
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

BUCKET_NAME = settings.report_bucket_name

router = APIRouter(prefix="/service-reports", tags=["service-reports"])

s3 = boto3.client("s3")

# helper function to upload file to S3 bucket
async def upload_to_s3(file: UploadFile, work_order_id: int) -> str:
    key = f"service-reports/{work_order_id}/{uuid.uuid4()}-{file.filename}"
    await run_in_threadpool(
        s3.upload_fileobj,
        file.file,
        BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": file.content_type},
    )
    return key

# POST endpoint for creating a new service report. Admin and Technician
@router.post("", response_model=ServiceReportRead)
async def create_service_report(
    work_order_id: int = Form(...),
    notes: str | None = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN, UserRole.FIELD_TECHNICIAN))
) -> ServiceReport:
    key = await upload_to_s3(file, work_order_id)
    report = ServiceReport(work_order_id=work_order_id, notes=notes, file_url=key)
    db.add(report)

    try:
        await db.commit()
    except Exception:
        await run_in_threadpool(s3.delete_object, Bucket=BUCKET_NAME, Key=key)
        raise
    await db.refresh(report)
    return report

# Endpoint to retrieve list of service reports:
@router.get("", response_model=list[ServiceReportRead])
async def list_service_reports(
    work_order_id: int | None = Query(
        default=None,
        description="Only list service reports for work orders of this ID"
    ),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
) -> list[ServiceReport]:
    statement = select(ServiceReport).order_by(ServiceReport.timestamp.desc())
    if work_order_id is not None:
        statement = statement.where(ServiceReport.work_order_id == work_order_id)
    result = await db.execute(statement)
    return result.scalars().all()
