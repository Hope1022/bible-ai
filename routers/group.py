from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.group import (
    GroupCreateSchema,
    GroupUpdateSchema,
    GroupResponseSchema,
    GroupDetailResponseSchema,
    JoinGroupSchema,
    MessageCreateSchema,
    MessageResponseSchema,
)
from services import group_service

router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
)


@router.post(
    "/",
    response_model=GroupResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_group(
    data: GroupCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await group_service.create_group(current_user.id, data, db)


@router.get("/me", response_model=list[GroupResponseSchema])
async def get_my_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await group_service.get_my_groups(current_user.id, db)


@router.get("/{group_id}", response_model=GroupDetailResponseSchema)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await group_service.get_group(group_id, current_user.id, db)


@router.post("/join", response_model=GroupResponseSchema)
async def join_group(
    data: JoinGroupSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await group_service.join_group(current_user.id, data, db)


@router.post("/{group_id}/leave", status_code=status.HTTP_200_OK)
async def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await group_service.leave_group(group_id, current_user.id, db)
    return {"message": "Left group successfully."}


@router.post(
    "/{group_id}/messages",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    group_id: int,
    data: MessageCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await group_service.send_message(group_id, current_user.id, data, db)


@router.get("/{group_id}/messages", response_model=list[MessageResponseSchema])
async def get_messages(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await group_service.get_messages(group_id, current_user.id, db)


@router.delete(
    "/{group_id}/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_message(
    group_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await group_service.delete_message(group_id, message_id, current_user.id, db)