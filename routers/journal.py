from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.journal import JournalCreateSchema, JournalUpdateSchema, JournalResponseSchema
from services import journal_service

router = APIRouter(
    prefix="/journals",
    tags=["Journals"],
)


@router.post(
    "/",
    response_model=JournalResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_journal(
    data: JournalCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await journal_service.create_journal(current_user.id, data, db)


@router.get("/me", response_model=list[JournalResponseSchema])
async def get_my_journals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await journal_service.get_my_journals(current_user.id, db)


@router.get("/{journal_id}", response_model=JournalResponseSchema)
async def get_journal(
    journal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await journal_service.get_journal(journal_id, current_user.id, db)


@router.patch("/{journal_id}", response_model=JournalResponseSchema)
async def update_journal(
    journal_id: int,
    data: JournalUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await journal_service.update_journal(journal_id, current_user.id, data, db)


@router.delete("/{journal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal(
    journal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await journal_service.delete_journal(journal_id, current_user.id, db)