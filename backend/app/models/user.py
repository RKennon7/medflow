from .base import Base
from .enums import UserRole
from sqlalchemy import String, Boolean
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    # fields: id, username, hashed_password, role, is_active
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        )
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return(f"User(id={self.id}, username={self.username!r}, role={self.role.value})")