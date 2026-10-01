from pydantic import BaseModel, ConfigDict

class DiscrepancyRead(BaseModel):
    work_order_id: int
    title: str
    equipment_hospital_id: int
    technician_hospital_id: int

    model_config = ConfigDict(from_attributes=True)