from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .work_order import WorkOrder

from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class ServiceReport(Base):
    __tablename__ = "service_reports"

    #fields: id, file_url, notes, timestamp
    id: Mapped[int] = mapped_column(primary_key=True)
    work_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_orders.id"))
    file_url: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # table relationships:
    work_order: Mapped["WorkOrder"] = relationship(back_populates="service_reports")

    #TODO __repr__