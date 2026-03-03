import os
from datetime import date
from uuid import UUID
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session
from openai import OpenAI
from openai import OpenAIError

from app.models.study_plan import StudyPlan
from app.services.base_service import BaseService
from app.services.productivity_service import productivity_service
from app.core.logger import get_logger

log = get_logger(__name__)


class StudyPlannerService(BaseService[StudyPlan]):
    model = StudyPlan

    def __init__(self):
        # BaseService initialization
        super().__init__()
        # Initialize OpenAI client if available
        api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def get_user_activity_context(self, db: Session, user_id: UUID) -> dict:
        """Call the existing productivity_service to get today's score & metrics."""
        return productivity_service.calculate_productivity_score(db, user_id)

    def generate_study_plan(self, db: Session, user_id: UUID) -> StudyPlan:
        """
        1. Fetch productivity context
        2. Build prompt
        3. Call OpenAI API (gpt-4o-mini)
        4. Generate fallback plan if OpenAI fails
        5. Save StudyPlan to DB
        6. Return created StudyPlan
        """
        context = self.get_user_activity_context(db, user_id)
        
        if not self.client:
            log.warning("OPENAI_API_KEY not set. Falling back to a standard generic study plan.")
            return self._generate_fallback_plan(db, user_id, context)

        tasks = context["tasks_completed_today"]
        habits = context["habits_completed_today"]
        study_hours = context["study_hours_today"]
        score = context["productivity_score"]

        prompt = f"""
You are an AI study coach.

User productivity today:
Score: {score}/100
Tasks completed: {tasks}
Habits completed: {habits}
Study hours: {study_hours}

Create a personalized, short, structured study plan for the rest of the day.

Focus on:
learning
revision
practice problems
healthy habits

Respond ONLY in a clean Markdown bullet list format. Do not add introductory or concluding chat phrases.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a concise, actionable planner outputting bullet points."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.7,
            )
            plan_text = response.choices[0].message.content.strip()
        except OpenAIError as e:
            log.error(f"OpenAI API Error creating plan: {e}")
            return self._generate_fallback_plan(db, user_id, context)

        return self._save_plan(db, user_id, plan_text)

    def _generate_fallback_plan(self, db: Session, user_id: UUID, context: dict) -> StudyPlan:
        """Generates a standard template study plan locally."""
        score = context["productivity_score"]
        
        if score > 70:
            plan_text = (
                "## Today's AI Study Plan\\n\\n"
                "- Review today's high-level notes for 30 minutes.\\n"
                "- Solve 2 advanced practice problems based on current material.\\n"
                "- Take a 15-minute healthy break as you've been working hard.\\n"
                "- Skim through tomorrow's lecture/chapter.\\n"
            )
        else:
            plan_text = (
                "## Today's AI Study Plan\\n\\n"
                "- Review missed basic concepts from yesterday for 45 minutes.\\n"
                "- Catch up on one incomplete habit (reading or exercise).\\n"
                "- Solve 3 foundational practice problems.\\n"
                "- Set up your study desk to be distraction-free for tomorrow.\\n"
            )

        return self._save_plan(db, user_id, plan_text)

    def _save_plan(self, db: Session, user_id: UUID, plan_text: str) -> StudyPlan:
        """Persists a new study plan to the DB, deleting older plans for today to keep it single per day, or simply inserting it."""
        today = date.today()
        
        # Build insertion data
        new_plan = StudyPlan(
            user_id=user_id,
            plan_text=plan_text,
            plan_date=today
        )
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        return new_plan

    def get_today_plan(self, db: Session, user_id: UUID) -> Optional[StudyPlan]:
        """Fetch the most recently generated study plan for today."""
        today = date.today()
        stmt = (
            select(StudyPlan)
            .where(
                StudyPlan.user_id == user_id,
                StudyPlan.plan_date == today
            )
            .order_by(StudyPlan.created_at.desc())
            .limit(1)
        )
        return db.scalar(stmt)

    def get_plan_history(self, db: Session, user_id: UUID, limit: int = 5) -> List[StudyPlan]:
        """Fetch historical study plans."""
        stmt = (
            select(StudyPlan)
            .where(StudyPlan.user_id == user_id)
            .order_by(StudyPlan.created_at.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())


study_planner_service = StudyPlannerService()
