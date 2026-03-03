import uuid
from datetime import datetime, date, timezone

from sqlalchemy import Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_text: Mapped[str] = mapped_column(Text, nullable=False)
    plan_date: Mapped[date] = mapped_column(
        Date, default=date.today, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # ─── Relationships ────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="study_plans")  # type: ignore[name-defined]

    # ─── Explicit named indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_study_plans_user_id", "user_id"),
        Index("ix_study_plans_plan_date", "plan_date"),
    )

    def __repr__(self) -> str:
        return f"<StudyPlan id={self.id} date={self.plan_date} user_id={self.user_id}>"
