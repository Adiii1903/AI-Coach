from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.services.base_service import BaseService
from app.core.logger import get_logger

log = get_logger(__name__)


class TaskService(BaseService[Task]):
    model = Task

    # ─── Task-specific queries ────────────────────────────────────────────────

    def get_user_tasks(self, db: Session, user_id: UUID) -> List[Task]:
        """Return all tasks for a user, newest first."""
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    def get_user_pending_tasks(self, db: Session, user_id: UUID) -> List[Task]:
        """Return incomplete tasks for a user, newest first."""
        stmt = (
            select(Task)
            .where(Task.user_id == user_id, Task.is_completed == False)  # noqa: E712
            .order_by(Task.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    def complete_task(self, db: Session, task_id: UUID) -> Task:
        """Mark a task as completed."""
        task = self.get_by_id(db, task_id)
        task.is_completed = True
        db.commit()
        db.refresh(task)
        log.info("Task marked complete: id={task_id}", task_id=task_id)
        return task


task_service = TaskService()
