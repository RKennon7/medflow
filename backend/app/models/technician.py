from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .work_order import WorkOrder
    from .hospital import Hospital

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Technician(Base):
    __tablename__ = "technicians"

    #fields: id, name, hospital_id
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    hospital_id: Mapped[int] = mapped_column(Integer, ForeignKey("hospitals.id"))

    # table relationships:
    hospital: Mapped["Hospital"] = relationship(back_populates="technicians")
    work_orders: Mapped["WorkOrder"] = relationship(back_populates="technician")

    #TODO __repr__
    