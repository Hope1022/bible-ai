from datetime import datetime
from pydantic import BaseModel, field_validator


class JournalCreateSchema(BaseModel):
    verse_reference: str | None = None
    content: str
    is_public: bool = False

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Journal entry must be at least 5 characters.")
        return value


class JournalUpdateSchema(BaseModel):
    content: str | None = None
    is_public: bool | None = None
    verse_reference: str | None = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Journal entry must be at least 5 characters.")
        return value


class JournalResponseSchema(BaseModel):
    id: int
    user_id: int
    verse_reference: str | None
    content: str
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}