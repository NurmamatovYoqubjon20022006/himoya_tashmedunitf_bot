"""SQLAlchemy modellari."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(StrEnum):
    USER = "user"
    PSYCHOLOGIST = "psychologist"
    LEGAL = "legal"
    COMMISSION = "commission"
    ADMIN = "admin"


class UserType(StrEnum):
    """Foydalanuvchi maqomi."""
    STUDENT = "student"      # Bakalavr talabasi
    MASTER = "master"        # Magistr
    TEACHER = "teacher"      # O'qituvchi
    STAFF = "staff"          # Universitet xodimi
    OTHER = "other"          # Boshqa


class Faculty(StrEnum):
    """TDTU Termiz filiali fakultetlari."""
    DAVOLASH_1 = "davolash_1"   # 1-son Davolash fakulteti
    DAVOLASH_2 = "davolash_2"   # 2-son Davolash fakulteti
    PEDIATRIYA = "pediatriya"   # Pediatriya fakulteti
    XALQARO = "xalqaro"         # Xalqaro ta'lim fakulteti


class ReportStatus(StrEnum):
    NEW = "new"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class IncidentType(StrEnum):
    HARASSMENT = "harassment"
    PRESSURE = "pressure"
    VIOLENCE = "violence"
    DISCRIMINATION = "discrimination"
    OTHER = "other"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64))
    language: Mapped[str] = mapped_column(String(2), default="uz")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="UserRole"), default=UserRole.USER
    )

    # Registratsiya ma'lumotlari
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    user_type: Mapped[UserType | None] = mapped_column(
        Enum(UserType, name="UserType")
    )
    faculty: Mapped[Faculty | None] = mapped_column(
        Enum(Faculty, name="Faculty")
    )
    course: Mapped[int | None] = mapped_column(Integer)
    direction: Mapped[str | None] = mapped_column(String(255))   # Yo'nalish (free text)
    group_name: Mapped[str | None] = mapped_column(String(64))   # Guruh raqami
    position: Mapped[str | None] = mapped_column(String(255))    # Lavozim (teacher/staff)

    is_registered: Mapped[bool] = mapped_column(default=False, server_default="false")
    registered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    is_blocked: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    reports: Mapped[list["Report"]] = relationship(back_populates="user")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    tracking_id: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    incident_type: Mapped[IncidentType] = mapped_column(Enum(IncidentType, name="IncidentType"))
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    incident_date: Mapped[str | None] = mapped_column(String(64))

    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="ReportStatus"), default=ReportStatus.NEW
    )
    admin_note: Mapped[str | None] = mapped_column(Text)

    is_anonymous: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User | None] = relationship(back_populates="reports")
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE")
    )
    file_id: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    report: Mapped[Report] = relationship(back_populates="attachments")


class AdminUser(Base):
    """Web admin panel foydalanuvchilari (Telegram'dan alohida)."""

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(128))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="UserRole"), default=UserRole.COMMISSION)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
