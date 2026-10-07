from typing import Literal

from pydantic import BaseModel

class CheckResult(BaseModel):
    status: Literal["ok", "unavailable"]
    error: str | None = None
    version: str | None = None # for DB
    bucket: str | None = None # for s3
    region: str | None = None # for s3

class HealthDetails(BaseModel):
    status: Literal["ok", "degraded"]
    database: CheckResult
    s3: CheckResult