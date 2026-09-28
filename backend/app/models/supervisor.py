from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .hospital import Hospital
    from .technician import Technician

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Supervisor(Base):
    __tablename__ = "supervisors"

    # fields: id, name
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # relationships: 1:1 hospital, 1:many technicians
    hospital: Mapped["Hospital"] = relationship(back_populates="supervisor")
    technicians: Mapped[list["Technician"]] = relationship(
        secondary="hospitals",
        primaryjoin="Supervisor.id == Hospital.supervisor_id",
        secondaryjoin="Hospital.id == Technician.hospital_id",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return(f"Supervisor(id={self.id}, name={self.name!r})")