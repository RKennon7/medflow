from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models import Hospital, Equipment, EquipmentStatus, Technician, Supervisor, User, WorkOrder, WorkOrderStatus
from app.schemas.hospital import MaintenanceFlag, TechnicianActiveWorkOrder, ReportingLineResult

router = APIRouter(prefix="/hospitals", tags=["hospitals"])

"""
Endpoint to answer business question 4:
Which hospitals have more than 30% of their equipment currently flagged for maintenance?
"""
@router.get("/maintenance", response_model=list[MaintenanceFlag])
async def get_maintenance_flags(
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user)
):
    maintenance_count = func.sum(case((Equipment.status == EquipmentStatus.MAINTENANCE, 1), else_=0))
    total_equipment = func.count(Equipment.id)
    maintenance_pct = maintenance_count * 100.0 / total_equipment

    statement = (
        select(
            Hospital.id.label("hospital_id"),
            Hospital.name.label("hospital_name"),
            maintenance_count.label("maintenance_count"),
            total_equipment.label("total_equipment"),
            maintenance_pct.label("maintenance_percent"),
        )
        .join(Equipment, Equipment.hospital_id == Hospital.id)
        .group_by(Hospital.id, Hospital.name)
        .having(maintenance_pct > 30)
        .order_by(Hospital.id)
    )

    result = await db.execute(statement)
    return [dict(row) for row in result.mappings().all()]

"""
Endpoint for business question #5:
How many technicians reporting to a specific Regional 
Biomed Supervisor have active work orders assigned to them?
"""
@router.get("/reporting-lines/{supervisor_id}", response_model=ReportingLineResult)
async def get_reporting_lines(
    supervisor_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    supervisor = await db.get(Supervisor, supervisor_id)
    if not supervisor:
        raise HTTPException(
            status_code=404,
            detail=f"supervisor {supervisor_id} not found",
        )

    statement = (
        select(
            Supervisor.id.label("supervisor_id"),
            Supervisor.name.label("supervisor_name"),
            Technician.id.label("technician_id"),
            Technician.name.label("technician_name"),
            func.count(WorkOrder.id).label("active_work_count"),
        )
        .join(Hospital, Hospital.supervisor_id == Supervisor.id)
        .join(Technician, Technician.hospital_id == Hospital.id)
        .outerjoin(
            WorkOrder,
            and_(
                WorkOrder.technician_id == Technician.id,
                WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.IN_PROGRESS]),
            ),
        )
        .where(Supervisor.id == supervisor_id)
        .group_by(Supervisor.id, Supervisor.name, Technician.id, Technician.name)
        .order_by(Technician.id)
    )

    result = await db.execute(statement)
    rows = result.mappings().all()
    technicians = [
        TechnicianActiveWorkOrder(
            technician_id=row.technician_id,
            technician_name=row.technician_name,
            active_work_count=row.active_work_count,
        ) for row in rows
    ]

    return ReportingLineResult(
        supervisor_id=supervisor.id,
        supervisor_name=supervisor.name,
        technician_count=len(technicians),
        technicians=technicians,
    )