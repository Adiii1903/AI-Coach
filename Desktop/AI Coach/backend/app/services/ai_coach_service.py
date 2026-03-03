import os
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from openai import OpenAI
from openai import OpenAIError

from app.models.ai_insight import AIInsight
from app.services.productivity_service import productivity_service
from app.core.logger import get_logger

log = get_logger(__name__)


class AICoachService:
    def __init__(self):
        # We instantiate the client here conditionally, assuming OPENAI_API_KEY is in env
        api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def get_user_activity_context(self, db: Session, user_id: UUID) -> dict:
        """Fetch today's activity using the productivity service."""
        return productivity_service.calculate_productivity_score(db, user_id)

    def generate_ai_advice(self, db: Session, user_id: UUID) -> AIInsight:
        """
        1. Fetch context
        2. Build AI prompt
        3. Call OpenAI
        4. Determine insight type
        5. Save and return insight
        """
        if not self.client:
            log.warning("OPENAI_API_KEY not set. Falling back to a mock insight.")
            return self._generate_mock_advice(db, user_id)

        # 1. Fetch context
        context = self.get_user_activity_context(db, user_id)
        tasks = context["tasks_completed_today"]
        habits = context["habits_completed_today"]
        study_hours = context["study_hours_today"]
        score = context["productivity_score"]

        # 2. Build AI prompt
        prompt = f"""
You are an AI productivity coach for students.

Today's activity:
Tasks completed: {tasks}
Habits completed: {habits}
Study hours: {study_hours}
Productivity score: {score} / 100

Give short advice (maximum 2 sentences) to improve or maintain productivity.
"""

        # 3. Call OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a concise, motivating productivity coach."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7,
            )
            insight_text = response.choices[0].message.content.strip()
        except OpenAIError as e:
            log.error(f"OpenAI API Error: {e}")
            return self._generate_mock_advice(db, user_id)

        # 4. Determine insight type
        if score < 40:
            insight_type = "warning"
        elif 40 <= score < 70:
            insight_type = "suggestion"
        else:
            insight_type = "motivation"

        # 5. Save insight
        insight = AIInsight(
            user_id=user_id,
            insight_text=insight_text,
            insight_type=insight_type
        )
        db.add(insight)
        db.commit()
        db.refresh(insight)

        return insight

    def _generate_mock_advice(self, db: Session, user_id: UUID) -> AIInsight:
        """Fallback when OpenAI is unavailable or errors out."""
        context = self.get_user_activity_context(db, user_id)
        score = context["productivity_score"]
        
        if score < 40:
            insight_type = "warning"
            text = "Your productivity score is quite low today. Try focusing on checking off at least one small task!"
        elif 40 <= score < 70:
            insight_type = "suggestion"
            text = "Solid effort today! Consider adding 30 minutes of focused study time to boost your score."
        else:
            insight_type = "motivation"
            text = "Incredible work today! You are crushing your goals, keep up the amazing momentum tomorrow."

        insight = AIInsight(
            user_id=user_id,
            insight_text=text,
            insight_type=insight_type
        )
        db.add(insight)
        db.commit()
        db.refresh(insight)
        return insight

    # Query helpers

    def get_latest_advice(self, db: Session, user_id: UUID) -> AIInsight | None:
        """Return the most recent AI insight for the user."""
        stmt = (
            select(AIInsight)
            .where(AIInsight.user_id == user_id)
            .order_by(AIInsight.created_at.desc())
            .limit(1)
        )
        return db.scalar(stmt)

    def get_advice_history(self, db: Session, user_id: UUID, limit: int = 5) -> list[AIInsight]:
        """Return the last `limit` insights for the user."""
        stmt = (
            select(AIInsight)
            .where(AIInsight.user_id == user_id)
            .order_by(AIInsight.created_at.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())


ai_coach_service = AICoachService()
