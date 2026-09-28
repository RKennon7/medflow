from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Base
from .enums import EquipmentStatus

if TYPE_CHECKING:
    from .hospital import Hospital
    from .work_order import WorkOrder

from decimal import Decimal
from sqlalchemy import Integer, String, ForeignKey, Numeric
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Equipment(Base):
    __tablename__ = "equipment"

    #fields: id, serial_number, model, status, charge_level, hospital_id

    id: Mapped[int] = mapped_column(primary_key=True)
    serial_number: Mapped[str] = mapped_column(String(50), unique=True)
    model: Mapped[str] = mapped_column(String(100))
    status: Mapped[EquipmentStatus] = mapped_column(
        SqlEnum(
            EquipmentStatus,
            name="equipment_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default = EquipmentStatus.IDLE,
    )
    charge_level: Mapped[Decimal] = mapped_column(Numeric(5,2))
    hospital_id: Mapped[int] = mapped_column(Integer, ForeignKey("hospitals.id"))

    #relationships:
    hospital: Mapped["Hospital"] = relationship(back_populates="equipment_list")
    work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="equipment")

    def __repr__(self) -> str:
        return(f"Equipment(serial={self.serial_number!r}, model={self.model!r}, "
               f"charge={self.charge_level}%, status={self.status}")
