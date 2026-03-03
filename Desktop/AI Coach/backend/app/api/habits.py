import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse
from app.services.auth_service import auth_service
from app.services.habit_service import habit_service
from app.utils.response import success_response

router = APIRouter(prefix="/habits", tags=["Habits"])
security = HTTPBearer()


# ─── Helper: Resolve & authorise habit ────────────────────────────────────────

def _get_owned_habit(habit_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    """Fetch habit by id and raise 403 if it doesn't belong to current_user."""
    habit = habit_service.get_by_id(db, habit_id)  # raises 404 if not found
    if habit.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this habit.",
        )
    return habit


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("")
def get_habits(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return all habits for the authenticated user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    habits = habit_service.get_user_habits(db, current_user.id)
    return success_response(
        [HabitResponse.model_validate(h).model_dump(mode="json") for h in habits]
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_habit(
    data: HabitCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Create a new habit for the authenticated user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    habit = habit_service.create(
        db,
        {
            "user_id": current_user.id,
            "name": data.name,
            "description": data.description,
            "target_frequency": data.target_frequency or "daily",
        },
    )
    return success_response(
        HabitResponse.model_validate(habit).model_dump(mode="json"),
        message="Habit created successfully.",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{habit_id}")
def update_habit(
    habit_id: uuid.UUID,
    data: HabitUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Update a habit (must be the owner)."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    _get_owned_habit(habit_id, current_user.id, db)

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    updated_habit = habit_service.update(db, habit_id, updates)
    return success_response(
        HabitResponse.model_validate(updated_habit).model_dump(mode="json"),
        message="Habit updated successfully.",
    )


@router.delete("/{habit_id}")
def delete_habit(
    habit_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Delete a habit (must be the owner)."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    _get_owned_habit(habit_id, current_user.id, db)
    habit_service.delete(db, habit_id)
    return success_response(None, message="Habit deleted successfully.")


@router.post("/{habit_id}/log")
def log_habit(
    habit_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Log today's completion for a habit and update streaks."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    # The habit service handles ownership checking and duplicates internally
    habit = habit_service.log_habit(db, habit_id, current_user.id)
    return success_response(
        HabitResponse.model_validate(habit).model_dump(mode="json"),
        message="Habit logged successfully.",
    )
