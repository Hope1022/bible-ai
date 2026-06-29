from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.mood import MoodCreateSchema, MoodResponseSchema
from services import mood_service

router = APIRouter(
    prefix="/moods",
    tags=["Moods"],
)


@router.post(
    "/",
    response_model=MoodResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def log_mood(
    data: MoodCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await mood_service.log_mood(current_user.id, data, db)


@router.get("/me", response_model=list[MoodResponseSchema])
async def get_my_moods(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await mood_service.get_my_moods(current_user.id, db)


@router.get("/me/latest", response_model=MoodResponseSchema | None)
async def get_latest_mood(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await mood_service.get_latest_mood(current_user.id, db)