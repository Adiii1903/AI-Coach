import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.auth_service import auth_service
from app.services.task_service import task_service
from app.utils.response import success_response

router = APIRouter(prefix="/tasks", tags=["Tasks"])
security = HTTPBearer()


# ─── Helper: Resolve & authorise task ────────────────────────────────────────

def _get_owned_task(task_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    """Fetch task by id and raise 403 if it doesn't belong to current_user."""
    task = task_service.get_by_id(db, task_id)  # raises 404 if not found
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task.",
        )
    return task


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("")
def get_tasks(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return all tasks for the authenticated user, newest first."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    tasks = task_service.get_user_tasks(db, current_user.id)
    return success_response(
        [TaskResponse.model_validate(t).model_dump(mode="json") for t in tasks]
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Create a new task for the authenticated user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    task = task_service.create(
        db,
        {
            "user_id": current_user.id,
            "title": data.title,
            "description": data.description,
            "priority": data.priority or "medium",
            "deadline": data.deadline,
        },
    )
    return success_response(
        TaskResponse.model_validate(task).model_dump(mode="json"),
        message="Task created successfully.",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{task_id}")
def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Update a task (must be the owner)."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    _get_owned_task(task_id, current_user.id, db)

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    updated_task = task_service.update(db, task_id, updates)
    return success_response(
        TaskResponse.model_validate(updated_task).model_dump(mode="json"),
        message="Task updated successfully.",
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Delete a task (must be the owner)."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    _get_owned_task(task_id, current_user.id, db)
    task_service.delete(db, task_id)
    return success_response(None, message="Task deleted successfully.")


@router.patch("/{task_id}/complete")
def complete_task(
    task_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Mark a task as completed (must be the owner)."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    _get_owned_task(task_id, current_user.id, db)
    task = task_service.complete_task(db, task_id)
    return success_response(
        TaskResponse.model_validate(task).model_dump(mode="json"),
        message="Task marked as completed.",
    )
