from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.models import Equipment, EquipmentStatus, User, UserRole, WorkOrder, WorkOrderStatus
from app.schemas.equipment import EquipmentRead, EquipmentCreate, EquipmentUpdate, ReliabilityRead

#singular equipment because there is no plural form of the word
router = APIRouter(prefix="/equipment", tags=["equipment"])

# get equipment list endpoint
@router.get("", response_model=list[EquipmentRead])
async def list_equipment(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
) -> list[Equipment]:
    statement = select(Equipment).where(Equipment.status != EquipmentStatus.OFFLINE)
    statement = statement.order_by(Equipment.id)

    result = await db.execute(statement)
    return list(result.scalars().all())

# post new equipment unit. Requires admin
@router.post("", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    payload: EquipmentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN))
) -> Equipment:
    equipment = Equipment(**payload.model_dump())
    db.add(equipment)
    await db.commit()
    await db.refresh(equipment)
    return equipment

#TODO add reliability router here, any user can view
@router.get("/reliability", response_model=list[ReliabilityRead])
async def get_model_reliability(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    statement = (
        select(
            Equipment.model.label("equipment_model"),
            func.count().filter(WorkOrder.status == WorkOrderStatus.COMPLETED).label("completed_count"),
            func.count().filter(WorkOrder.status == WorkOrderStatus.FAILED).label("failed_count"),
        )
        .join(WorkOrder, Equipment.id == WorkOrder.equipment_id)
        .where(WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.FAILED]))
        .group_by(Equipment.model)
        .order_by(Equipment.model)
    )

    result = await db.execute(statement)
    return result.mappings().all()


# get equipment by id:
@router.get("/{equipment_id}", response_model=EquipmentRead)
async def get_equipment(
    equipment_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
) -> Equipment:
    equipment = await db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment with id {equipment_id} not found.",
        )
    return equipment

# delete equipment: requires admin
@router.delete("/{equipment_id}")
async def delete_equipment(
    equipment_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN))
):
    equipment = await db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment with id {equipment_id} not found.",
        )
    await db.delete(equipment)
    await db.commit()
    return {"message": "Item deleted successfully"}

# update equipment by id: requires admin
@router.patch("/{equipment_id}", response_model=EquipmentRead)
async def update_equipment(
    equipment_id: int,
    payload: EquipmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.CLINICAL_ADMIN))
) -> Equipment:
    equipment = await db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment with id {equipment_id} not found.",
        )

    # get fields provided in the request payload
    update_data = payload.model_dump(exclude_unset=True)

    # apply updates to equipment object:
    for field, value in update_data.items():
        setattr(equipment, field, value)

    await db.commit()
    await db.refresh(equipment)
    return equipment
    