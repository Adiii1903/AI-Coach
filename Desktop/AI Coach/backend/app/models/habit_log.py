import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    habit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ─── Relationships ────────────────────────────────────────────────────────
    habit: Mapped["Habit"] = relationship("Habit", back_populates="logs")  # type: ignore[name-defined]

    # ─── Constraints ──────────────────────────────────────────────────────────
    # A habit can only be logged once per day
    __table_args__ = (
        UniqueConstraint("habit_id", "log_date", name="uix_habit_log_date"),
    )

    def __repr__(self) -> str:
        return f"<HabitLog id={self.id} habit_id={self.habit_id} date={self.log_date}>"
