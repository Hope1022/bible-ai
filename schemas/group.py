from datetime import datetime
from pydantic import BaseModel, field_validator
from models.group_member import GroupMemberRole


class GroupCreateSchema(BaseModel):
    name: str
    description: str | None = None
    max_members: int = 50

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Group name must be at least 3 characters.")
        if len(value) > 100:
            raise ValueError("Group name must be under 100 characters.")
        return value

    @field_validator("max_members")
    @classmethod
    def validate_max_members(cls, value: int) -> int:
        if value < 2 or value > 500:
            raise ValueError("Max members must be between 2 and 500.")
        return value


class GroupUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    max_members: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Group name must be at least 3 characters.")
        return value


class GroupMemberResponseSchema(BaseModel):
    user_id: int
    role: GroupMemberRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class GroupResponseSchema(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str | None
    invite_code: str
    max_members: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class GroupDetailResponseSchema(GroupResponseSchema):
    members: list[GroupMemberResponseSchema] = []


class JoinGroupSchema(BaseModel):
    invite_code: str


class MessageCreateSchema(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 1:
            raise ValueError("Message cannot be empty.")
        if len(value) > 2000:
            raise ValueError("Message cannot exceed 2000 characters.")
        return value


class MessageResponseSchema(BaseModel):
    id: int
    group_id: int
    user_id: int
    content: str
    is_deleted: bool
    created_at: datetime

    model_config = {"from_attributes": True}