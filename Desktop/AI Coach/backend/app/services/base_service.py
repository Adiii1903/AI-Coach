from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.core.logger import get_logger

log = get_logger(__name__)

# Generic type bound to any SQLAlchemy model
ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """
    Generic CRUD base service.

    Concrete services should subclass this and set the `model` class attribute:

        class TaskService(BaseService[Task]):
            model = Task
    """

    model: Type[ModelType]

    # ─── Create ───────────────────────────────────────────────────────────────

    def create(self, db: Session, data: Dict[str, Any]) -> ModelType:
        """Instantiate, persist, and return a new model instance."""
        instance = self.model(**data)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        log.info(
            "Created {model} id={id}",
            model=self.model.__name__,
            id=getattr(instance, "id", "?"),
        )
        return instance

    # ─── Read ─────────────────────────────────────────────────────────────────

    def get_by_id(self, db: Session, record_id: Any) -> ModelType:
        """Return a single record by primary key, or raise 404."""
        instance = db.scalar(
            select(self.model).where(getattr(self.model, 'id') == record_id)
        )
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id={record_id} not found.",
            )
        return instance

    def get_all(
        self,
        db: Session,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ModelType]:
        """
        Return a list of records, optionally filtered by exact column matches.

        Example:
            service.get_all(db, filters={"user_id": user.id})
        """
        stmt = select(self.model)

        if filters:
            for column, value in filters.items():
                col_attr = getattr(self.model, column, None)
                if col_attr is not None:
                    stmt = stmt.where(col_attr == value)

        stmt = stmt.offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    # ─── Update ───────────────────────────────────────────────────────────────

    def update(
        self, db: Session, record_id: Any, data: Dict[str, Any]
    ) -> ModelType:
        """
        Partial-update a record by primary key.

        Only keys present in `data` are written — unknown column names
        raise a 400 rather than silently being ignored.
        """
        instance = self.get_by_id(db, record_id)

        for key, value in data.items():
            if not hasattr(instance, key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{key}' is not a valid field on {self.model.__name__}.",
                )
            setattr(instance, key, value)

        db.commit()
        db.refresh(instance)
        log.info(
            "Updated {model} id={id}",
            model=self.model.__name__,
            id=record_id,
        )
        return instance

    # ─── Delete ───────────────────────────────────────────────────────────────

    def delete(self, db: Session, record_id: Any) -> None:
        """Delete a record by primary key. Raises 404 if not found."""
        instance = self.get_by_id(db, record_id)
        db.delete(instance)
        db.commit()
        log.info(
            "Deleted {model} id={id}",
            model=self.model.__name__,
            id=record_id,
        )
