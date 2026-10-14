import uuid, boto3
import logging
from botocore.exceptions import ClientError
from botocore.config import Config
from app.config import settings
from app.dependencies import get_db, get_current_user, require_role
from app.models import User, UserRole, ServiceReport
from app.schemas.service_report import ServiceReportCreate, ServiceReportRead, ServiceReportFileUrl
from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

BUCKET_NAME = settings.report_bucket_name

router = APIRouter(prefix="/service-reports", tags=["service-reports"])

s3 = boto3.client(
    "s3",
    region_name="us-east-2",
    config=Config(signature_version="s3v4"),
    )

logger = logging.getLogger(__name__)

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

# endpoint to delete a service report. requires admin
# deletes the db record and deletes the file from the s3 bucket
@router.delete("/{report_id}")
async def delete_service_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN))
):
    report = await db.get(ServiceReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Service report not found")

    # get key before deleting record
    key = report.file_url
    await db.delete(report)
    await db.commit()

    try:
        await run_in_threadpool(s3.delete_object, Bucket=BUCKET_NAME, Key=key)
    except ClientError:
        logger.exception("Deleted report %s but failed to delete S3 object %s", report_id, key)

    return {"message": "Item deleted successfully"}


# endpoint to return a presigned file url for a specific service report ID
@router.get("/{report_id}/file", response_model=ServiceReportFileUrl)
async def get_service_report_file(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    report = await db.get(ServiceReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Service report not found")

    expires_in = 300

    # check if key points to a real object in the S3 bucket
    try:
        await run_in_threadpool(s3.head_object, Bucket=BUCKET_NAME, Key=report.file_url)
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            raise HTTPException(status_code=404, detail="File not found in storage")
        raise HTTPException(status_code=502, detail="Could not check file")

    # generate a presigned url for viewing the file
    try:
        url = await run_in_threadpool(
            s3.generate_presigned_url,
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": report.file_url},
            ExpiresIn=expires_in,
        )
    except ClientError:
        raise HTTPException(status_code=502, detail="Could not generate file link")

    return ServiceReportFileUrl(url=url, expires_in=expires_in)
