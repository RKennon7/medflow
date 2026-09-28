from enum import Enum

class EquipmentStatus(str, Enum):
    # available, in-use, maintenance, offline
    IDLE = "Idle"
    IN_USE = "In-Use"
    MAINTENANCE = "Maintenance"
    OFFLINE = "Offline"

class WorkOrderPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    CRITICAL = "Critical"

class WorkOrderStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In-Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class UserRole(str, Enum):
    CLINICAL_ADMIN = "Clinical Admin"
    FIELD_TECHNICIAN = "Field Technician"
    AUDITOR = "Auditor"