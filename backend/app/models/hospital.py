"""
fields: id, name, location_region, capacity, supervisor_id
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .equipment import Equipment
    from .technician import Technician
    from .supervisor import Supervisor

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    location_region: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[int] = mapped_column(Integer)
    supervisor_id: Mapped[int] = mapped_column(Integer, ForeignKey("supervisors.id"))

    # relationships:
    equipment_list: Mapped[list["Equipment"]] = relationship(back_populates = "hospital")
    technicians: Mapped[list["Technician"]] = relationship(back_populates = "hospital")
    supervisor: Mapped["Supervisor"] = relationship(back_populates="hospital")


    def __repr__(self) -> str:
        return(f"Hospital(id={self.id}, name={self.name!r}, region={self.location_region!r})")