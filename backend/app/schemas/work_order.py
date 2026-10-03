from pydantic import BaseModel, ConfigDict
from app.models import WorkOrderPriority, WorkOrderStatus

class WorkOrderRead(BaseModel):
    id: int
    title: str
    priority: WorkOrderPriority
    status: WorkOrderStatus
    equipment_id: int
    technician_id: int

    model_config = ConfigDict(from_attributes=True)

class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatus

class DiscrepancyRead(BaseModel):
    work_order_id: int
    title: str
    equipment_hospital_id: int
    technician_hospital_id: int

    model_config = ConfigDict(from_attributes=True)