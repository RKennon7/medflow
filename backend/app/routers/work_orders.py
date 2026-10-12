from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.models import WorkOrder, WorkOrderPriority, Equipment, Technician, User, UserRole
from app.schemas.work_order import DiscrepancyRead, WorkOrderRead, WorkOrderStatusUpdate, WorkOrderUpdate, WorkOrderCreate

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

# create new work order, requires admin
@router.post("", response_model=WorkOrderRead)
async def create_work_order(
    payload: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN))
) -> WorkOrder:
    work_order = WorkOrder(**payload.model_dump())
    db.add(work_order)
    await db.commit()
    await db.refresh(work_order)
    return work_order

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


# update work order, requires admin
@router.patch("/{work_order_id}", response_model=WorkOrderRead)
async def update_work_order(
    work_order_id: int,
    payload: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
) -> WorkOrder:
    work_order = await db.get(WorkOrder, work_order_id)
    if work_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order with id {work_order_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(work_order, field, value)

    await db.commit()
    await db.refresh(work_order)
    return work_order

# delete a work order: requires admin
@router.delete("/{work_order_id}")
async def delete_work_order(
    work_order_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN))
):
    work_order = await db.get(WorkOrder, work_order_id)
    if work_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order with id {work_order_id} not found.",
        )
    await db.delete(work_order)
    await db.commit()
    return {"message": "Item deleted successfully"}

# technician endpoint to update work order status:
@router.patch("/{work_order_id}/status", response_model=WorkOrderRead)
async def update_work_order_status(
    work_order_id: int,
    payload: WorkOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FIELD_TECHNICIAN))
) -> WorkOrder:
    work_order = await db.get(WorkOrder, work_order_id)
    if work_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order with id {work_order_id} not found.",
        )

    work_order.status = payload.status
    await db.commit()
    await db.refresh(work_order)
    return work_order