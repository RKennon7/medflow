from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ServiceReportCreate(BaseModel):
    work_order_id: int
    notes: str | None = None

class ServiceReportRead(BaseModel):
    id: int
    work_order_id: int
    file_url: str
    notes: str | None = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)