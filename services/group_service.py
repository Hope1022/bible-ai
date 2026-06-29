from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from models.group import Group
from models.group_member import GroupMember, GroupMemberRole
from models.message import Message
from schemas.group import (
    GroupCreateSchema,
    GroupUpdateSchema,
    GroupResponseSchema,
    GroupDetailResponseSchema,
    JoinGroupSchema,
    MessageCreateSchema,
    MessageResponseSchema,
)
from core.exceptions import (
    ResourceNotFoundException,
    InsufficientPermissionsException,
    AlreadyMemberException,
    GroupFullException,
    BadRequestException,
)


async def create_group(
    user_id: int,
    data: GroupCreateSchema,
    db: AsyncSession,
) -> GroupResponseSchema:
    group = Group(
        owner_id=user_id,
        name=data.name,
        description=data.description,
        max_members=data.max_members,
    )
    db.add(group)
    await db.flush()

    member = GroupMember(
        group_id=group.id,
        user_id=user_id,
        role=GroupMemberRole.leader,
    )
    db.add(member)
    await db.commit()

    return GroupResponseSchema.model_validate(group)


async def get_my_groups(
    user_id: int,
    db: AsyncSession,
) -> list[GroupResponseSchema]:
    result = await db.execute(
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.user_id == user_id)
        .order_by(Group.created_at.desc())
    )
    groups = result.scalars().all()
    return [GroupResponseSchema.model_validate(g) for g in groups]


async def get_group(
    group_id: int,
    user_id: int,
    db: AsyncSession,
) -> GroupDetailResponseSchema:
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalars().first()

    if not group:
        raise ResourceNotFoundException

    member_result = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id)
    )
    members = member_result.scalars().all()

    is_member = any(m.user_id == user_id for m in members)
    if not is_member:
        raise InsufficientPermissionsException

    return GroupDetailResponseSchema.model_validate(group)


async def join_group(
    user_id: int,
    data: JoinGroupSchema,
    db: AsyncSession,
) -> GroupResponseSchema:
    result = await db.execute(
        select(Group).where(Group.invite_code == data.invite_code)
    )
    group = result.scalars().first()

    if not group:
        raise ResourceNotFoundException

    existing = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == user_id,
        )
    )
    if existing.scalars().first():
        raise AlreadyMemberException

    count_result = await db.execute(
        select(func.count()).where(GroupMember.group_id == group.id)
    )
    member_count = count_result.scalar()

    if member_count >= group.max_members:
        raise GroupFullException

    member = GroupMember(
        group_id=group.id,
        user_id=user_id,
        role=GroupMemberRole.member,
    )
    db.add(member)
    await db.commit()

    return GroupResponseSchema.model_validate(group)


async def leave_group(
    group_id: int,
    user_id: int,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
    )
    member = result.scalars().first()

    if not member:
        raise ResourceNotFoundException

    group_result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = group_result.scalars().first()

    if group and group.owner_id == user_id:
        raise BadRequestException

    await db.delete(member)
    await db.commit()


async def send_message(
    group_id: int,
    user_id: int,
    data: MessageCreateSchema,
    db: AsyncSession,
) -> MessageResponseSchema:
    member_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
    )
    if not member_result.scalars().first():
        raise InsufficientPermissionsException

    message = Message(
        group_id=group_id,
        user_id=user_id,
        content=data.content,
    )
    db.add(message)
    await db.commit()

    return MessageResponseSchema.model_validate(message)


async def get_messages(
    group_id: int,
    user_id: int,
    db: AsyncSession,
    limit: int = 50,
) -> list[MessageResponseSchema]:
    member_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
    )
    if not member_result.scalars().first():
        raise InsufficientPermissionsException

    result = await db.execute(
        select(Message)
        .where(Message.group_id == group_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [MessageResponseSchema.model_validate(m) for m in messages]


async def delete_message(
    group_id: int,
    message_id: int,
    user_id: int,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.group_id == group_id,
        )
    )
    message = result.scalars().first()

    if not message:
        raise ResourceNotFoundException

    if message.user_id != user_id:
        raise InsufficientPermissionsException

    message.is_deleted = True
    message.content = ""
    await db.commit()