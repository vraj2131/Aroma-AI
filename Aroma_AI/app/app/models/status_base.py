import enum as PyEnum

# ---------------------------
# ENUMS
# ---------------------------
class UserRole(PyEnum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"

class StatusEnum(PyEnum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    

class OrderStatusEnum(PyEnum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"