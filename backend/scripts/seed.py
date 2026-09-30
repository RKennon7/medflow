import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Base, Equipment, Hospital, WorkOrder, ServiceReport, Supervisor, Technician, EquipmentStatus, WorkOrderPriority, WorkOrderStatus
from app.database import AsyncSessionLocal

async def seed_database():
    async with AsyncSessionLocal() as session:
        hospitals = [
            Hospital(name="Weenie Hut General", location_region="US-Midwest",capacity=40, supervisor_id=101),
            Hospital(name="Cherguson Medical Center", location_region="US-South", capacity=25, supervisor_id=102)
        ]

        equipment = [
            Equipment(id=1, serial_number="XR-1001", model="Siemens Mobilett Elara Max X-Ray", charge_level=18.5, hospital_id=1, status=EquipmentStatus.IN_USE),
            Equipment(id=2, serial_number="VN-3001", model="Philips Respironics V60 Ventilator", charge_level=76.0, hospital_id=1, status=EquipmentStatus.AVAILABLE),
            Equipment(id=3, serial_number="DF-2050", model="Zoll R Series Defibrillator", charge_level=9.0, hospital_id=2, status=EquipmentStatus.IN_USE),
            Equipment(id=4, serial_number="US-4001", model="GE Venue Go Ultrasound", charge_level=42.0, hospital_id=2, status=EquipmentStatus.MAINTENANCE),
            Equipment(id=5, serial_number="XR-1002", model="Siemens Mobilett Elara Max X-Ray", charge_level=18.5, hospital_id=2, status=EquipmentStatus.MAINTENANCE),
            Equipment(id=6, serial_number="VN-3002", model="Philips Respironics V60 Ventilator", charge_level=76.0, hospital_id=2, status=EquipmentStatus.AVAILABLE),
            Equipment(id=7, serial_number="DF-2069", model="Zoll R Series Defibrillator", charge_level=25.0, hospital_id=1, status=EquipmentStatus.IN_USE),
            Equipment(id=8, serial_number="US-4002", model="GE Venue Go Ultrasound", charge_level=84.0, hospital_id=1, status=EquipmentStatus.MAINTENANCE),
        ]

        technicians = [
            Technician(id=201, name="Gill Gilliam", hospital_id=1),
            Technician(id=202, name="Da Bob", hospital_id=1),
            Technician(id=203, name="Birdie Jones", hospital_id=2),
            Technician(id=204, name="Slacker", hospital_id=2)
        ]

        supervisors = [
            Supervisor(id=101, name="Dr. Movie"),
            Supervisor(id=102, name="Bert Cherguson Jr.")
        ]

        work_orders = [
            WorkOrder(id=1, title="Portable Chest X-Ray Imaging", priority=WorkOrderPriority.CRITICAL, equipment_id=1, technician_id=201),
            WorkOrder(id=2, title="Defibrillator Readiness Check", priority=WorkOrderPriority.LOW, equipment_id=3, technician_id=202),
            WorkOrder(id=3, title="Probe Replacement + Recalibration", priority=WorkOrderPriority.CRITICAL, status=WorkOrderStatus.COMPLETED, equipment_id=4, technician_id=201),
            WorkOrder(id=4, title="Probe Replacement + Recalibration", priority=WorkOrderPriority.CRITICAL, status=WorkOrderStatus.IN_PROGRESS, equipment_id=8, technician_id=204),
            WorkOrder(id=5, title="Detector Panel Cleaning", priority=WorkOrderPriority.LOW, status=WorkOrderStatus.COMPLETED, equipment_id=5, technician_id=203),
            WorkOrder(id=6, title="Battery Discharge Test", priority=WorkOrderPriority.MEDIUM, status=WorkOrderStatus.COMPLETED, equipment_id=7, technician_id=202),
            WorkOrder(id=7, title="Battery Discharge Test", priority=WorkOrderPriority.MEDIUM, status=WorkOrderStatus.FAILED, equipment_id=3, technician_id=204),
            WorkOrder(id=8, title="Ventilator Circuit + Filter Change", priority=WorkOrderPriority.MEDIUM, status=WorkOrderStatus.COMPLETED, equipment_id=2, technician_id=202),
            WorkOrder(id=9, title="Ventilator Circuit + Filter Change", priority=WorkOrderPriority.CRITICAL, status=WorkOrderStatus.COMPLETED, equipment_id=6, technician_id=204),
        ]

        reports = [
            ServiceReport(id=1, work_order_id=1, file_url="s3://medflow-diagnostics/jd1001-001.pdf", 
            notes="mysterious goop leak patched")
        ]

        session.add_all(hospitals + equipment + technicians + supervisors + work_orders + reports)
        await session.commit()
        await sync_all_sequences(session, ["hospitals", "equipment", "work_orders", "technicians", "service_reports", "supervisors"])

async def sync_all_sequences(session: AsyncSession, tables: list[str]):
    for table in tables:
        # pg_get_serial_sequence automatically finds the correct sequence name
        query = text(f"""
            SELECT setval(
                pg_get_serial_sequence('{table}', 'id'),
                COALESCE((SELECT MAX(id) FROM {table}), 1)
            );
        """)
        await session.execute(query)

    await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_database())
