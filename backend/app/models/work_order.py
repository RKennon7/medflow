from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Base
from .enums import WorkOrderPriority, WorkOrderStatus

if TYPE_CHECKING:
    from .technician import Technician
    from .equipment import Equipment
    from .service_report import ServiceReport

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship


class WorkOrder(Base):
    __tablename__ = "work_orders"

    #id, title, priority, status, equipment_id, technician_id
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    priority: Mapped[WorkOrderPriority] = mapped_column(
        SqlEnum(
            WorkOrderPriority,
            name="work_order_priority",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            )
        )
    status: Mapped[WorkOrderStatus] = mapped_column(
        SqlEnum(
            WorkOrderStatus,
            name="work_order_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=WorkOrderStatus.PENDING,
    )
    equipment_id: Mapped[int] = mapped_column(Integer, ForeignKey("equipment.id"))
    technician_id: Mapped[int] = mapped_column(Integer, ForeignKey("technicians.id"))

    # table relationships:
    equipment: Mapped["Equipment"] = relationship(back_populates="work_orders")
    technician: Mapped["Technician"] = relationship(back_populates="work_orders")
    service_reports: Mapped["ServiceReport"] = relationship(back_populates="work_order")

    # todo __repr__
