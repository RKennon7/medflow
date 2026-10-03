from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models import WorkOrder, WorkOrderPriority, Equipment, Technician, User
from app.schemas.work_order import DiscrepancyRead, WorkOrderRead, WorkOrderStatusUpdate

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

# list all work orders:
@router.get("", response_model=list[WorkOrderRead])
async def list_work_orders(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
) -> list[WorkOrder]:
    statement = select(WorkOrder).order_by(WorkOrder.id)
    result = await db.execute(statement)
    return list(result.scalars().all())

"""
route to return co-location discrepancies between technician and equipment location
"""
@router.get("/discrepancies", response_model=list[DiscrepancyRead])
async def get_colocation_discrepancies(
    priority: WorkOrderPriority | None = Query(
        default=None,
        description="Only list discrepancies for work orders of this priority"
    ),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    statement = (
        select(
            WorkOrder.id.label("work_order_id"),
            WorkOrder.title,
            Equipment.hospital_id.label("equipment_hospital_id"),
            Technician.hospital_id.label("technician_hospital_id")
        )
        .join(Equipment, Equipment.id == WorkOrder.equipment_id)
        .join(Technician, Technician.id == WorkOrder.technician_id)
        .where(Equipment.hospital_id != Technician.hospital_id)
    )

    if priority is not None:
        statement = statement.where(WorkOrder.priority == priority)

    statement = statement.order_by(WorkOrder.id)

    result = await db.execute(statement)
    return [dict(row) for row in result.mappings().all()]