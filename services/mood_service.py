from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.mood_log import MoodLog
from schemas.mood import MoodCreateSchema, MoodResponseSchema


async def log_mood(
    user_id: int,
    data: MoodCreateSchema,
    db: AsyncSession,
) -> MoodResponseSchema:
    mood = MoodLog(
        user_id=user_id,
        mood_score=data.mood_score,
        note=data.note,
    )
    db.add(mood)
    await db.commit()
    return MoodResponseSchema.model_validate(mood)


async def get_my_moods(
    user_id: int,
    db: AsyncSession,
    limit: int = 30,
) -> list[MoodResponseSchema]:
    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == user_id)
        .order_by(MoodLog.created_at.desc())
        .limit(limit)
    )
    moods = result.scalars().all()
    return [MoodResponseSchema.model_validate(m) for m in moods]


async def get_latest_mood(
    user_id: int,
    db: AsyncSession,
) -> MoodResponseSchema | None:
    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == user_id)
        .order_by(MoodLog.created_at.desc())
        .limit(1)
    )
    mood = result.scalars().first()
    if not mood:
        return None
    return MoodResponseSchema.model_validate(mood)