from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from app.models import EquipmentStatus

class EquipmentBase(BaseModel):
    serial_number: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    status: EquipmentStatus = EquipmentStatus.AVAILABLE
    charge_level: Decimal = Field(ge=0, le=100)
    hospital_id: int

class EquipmentCreate(EquipmentBase):
    """shape of request body for POST /equipment"""

class EquipmentRead(EquipmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class EquipmentUpdate(BaseModel):
    serial_number: str | None = Field(min_length=1, max_length=50, default=None)
    model: str | None = Field(min_length=1, max_length=50, default=None)
    status: EquipmentStatus | None = None
    charge_level: Decimal | None = Field(ge=0, le=100, default=None)
    hospital_id: int | None

class ReliabilityRead(BaseModel):
    equipment_model: str
    completed_count: int
    failed_count: int