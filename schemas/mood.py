from datetime import datetime
from pydantic import BaseModel, field_validator


class MoodCreateSchema(BaseModel):
    mood_score: int
    note: str | None = None

    @field_validator("mood_score")
    @classmethod
    def validate_mood_score(cls, value: int) -> int:
        if value < 1 or value > 5:
            raise ValueError("Mood score must be between 1 and 5.")
        return value


class MoodResponseSchema(BaseModel):
    id: int
    user_id: int
    mood_score: int
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}