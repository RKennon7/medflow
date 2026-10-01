from pydantic import BaseModel, ConfigDict

class MaintenanceFlag(BaseModel):
    hospital_id: int
    hospital_name: str
    total_equipment: int
    maintenance_count: int
    maintenance_percent: float

    model_config = ConfigDict(from_attributes=True)

class TechnicianActiveWorkOrder(BaseModel):
    technician_id: int
    technician_name: str
    active_work_count: int

class ReportingLineResult(BaseModel):
    supervisor_id: int
    supervisor_name: str
    technician_count: int
    technicians: list[TechnicianActiveWorkOrder]