from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.streak import StreakResponseSchema, MarkReadResponseSchema
from services import streak_service

router = APIRouter(
    prefix="/streaks",
    tags=["Streaks"],
)


@router.get("/me", response_model=StreakResponseSchema)
async def get_my_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await streak_service.get_streak(current_user.id, db)


@router.post("/mark-read", response_model=MarkReadResponseSchema)
async def mark_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await streak_service.mark_read(current_user.id, db)