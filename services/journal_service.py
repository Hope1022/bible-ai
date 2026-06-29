from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.journal import Journal
from schemas.journal import JournalCreateSchema, JournalUpdateSchema, JournalResponseSchema
from core.exceptions import ResourceNotFoundException, InsufficientPermissionsException


async def create_journal(
    user_id: int,
    data: JournalCreateSchema,
    db: AsyncSession,
) -> JournalResponseSchema:
    journal = Journal(
        user_id=user_id,
        verse_reference=data.verse_reference,
        content=data.content,
        is_public=data.is_public,
    )
    db.add(journal)
    await db.commit()
    return JournalResponseSchema.model_validate(journal)


async def get_my_journals(
    user_id: int,
    db: AsyncSession,
) -> list[JournalResponseSchema]:
    result = await db.execute(
        select(Journal)
        .where(Journal.user_id == user_id)
        .order_by(Journal.created_at.desc())
    )
    journals = result.scalars().all()
    return [JournalResponseSchema.model_validate(j) for j in journals]


async def get_journal(
    journal_id: int,
    user_id: int,
    db: AsyncSession,
) -> JournalResponseSchema:
    result = await db.execute(
        select(Journal).where(Journal.id == journal_id)
    )
    journal = result.scalars().first()

    if not journal:
        raise ResourceNotFoundException

    if not journal.is_public and journal.user_id != user_id:
        raise InsufficientPermissionsException

    return JournalResponseSchema.model_validate(journal)


async def update_journal(
    journal_id: int,
    user_id: int,
    data: JournalUpdateSchema,
    db: AsyncSession,
) -> JournalResponseSchema:
    result = await db.execute(
        select(Journal).where(Journal.id == journal_id)
    )
    journal = result.scalars().first()

    if not journal:
        raise ResourceNotFoundException

    if journal.user_id != user_id:
        raise InsufficientPermissionsException

    if data.content is not None:
        journal.content = data.content
    if data.is_public is not None:
        journal.is_public = data.is_public
    if data.verse_reference is not None:
        journal.verse_reference = data.verse_reference

    await db.commit()
    return JournalResponseSchema.model_validate(journal)


async def delete_journal(
    journal_id: int,
    user_id: int,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(Journal).where(Journal.id == journal_id)
    )
    journal = result.scalars().first()

    if not journal:
        raise ResourceNotFoundException

    if journal.user_id != user_id:
        raise InsufficientPermissionsException

    await db.delete(journal)
    await db.commit()