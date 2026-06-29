from datetime import datetime, date
from pydantic import BaseModel


class MarkReadSchema(BaseModel):
    pass


class StreakResponseSchema(BaseModel):
    current_streak: int
    longest_streak: int
    last_read_date: date | None
    updated_at:     datetime

    model_config = {"from_attributes": True}


class MarkReadResponseSchema(BaseModel):
    message: str
    streak:  StreakResponseSchema