from pydantic import BaseModel, ConfigDict
from app.models import WorkOrderPriority, WorkOrderStatus

class WorkOrderBase(BaseModel):
    title: str
    priority: WorkOrderPriority
    status: WorkOrderStatus
    equipment_id: int
    technician_id: int

class WorkOrderCreate(WorkOrderBase):
    """request body for POST/work-orders"""

class WorkOrderRead(WorkOrderBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatus

class WorkOrderUpdate(BaseModel):
    title: str | None = None
    priority: WorkOrderPriority | None = None
    status: WorkOrderStatus | None = None
    equipment_id: int | None = None
    technician_id: int | None = None

class DiscrepancyRead(BaseModel):
    work_order_id: int
    title: str
    equipment_hospital_id: int
    technician_hospital_id: int

    model_config = ConfigDict(from_attributes=True)