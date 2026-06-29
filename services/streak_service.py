from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.streak import Streak
from schemas.streak import StreakResponseSchema, MarkReadResponseSchema


async def get_or_create_streak(
    user_id: int,
    db: AsyncSession,
) -> Streak:

    result = await db.execute(
        select(Streak).where(Streak.user_id == user_id)
    )
    streak = result.scalars().first()

    if streak is None:
        streak = Streak(user_id=user_id)
        db.add(streak)
        await db.flush()

    return streak


async def get_streak(
    user_id: int,
    db: AsyncSession,
) -> StreakResponseSchema:

    streak = await get_or_create_streak(user_id, db)
    await db.commit()
    return StreakResponseSchema.model_validate(streak)


async def mark_read(
    user_id: int,
    db: AsyncSession,
) -> MarkReadResponseSchema:

    streak = await get_or_create_streak(user_id, db)

    today     = date.today()
    yesterday = today - timedelta(days=1)

    if streak.last_read_date == today:
        await db.commit()
        return MarkReadResponseSchema(
            message="Already marked today. Come back tomorrow!",
            streak=StreakResponseSchema.model_validate(streak),
        )

    if streak.last_read_date is None:
        streak.current_streak = 1
        streak.longest_streak = 1
        streak.last_read_date = today
        message = "Your streak has begun! Day 1."

    elif streak.last_read_date == yesterday:
        streak.current_streak += 1
        streak.last_read_date  = today

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
            message = f"New record! Day {streak.current_streak}."
        else:
            message = f"Day {streak.current_streak}! Keep going."

    else:
        streak.current_streak = 1
        streak.last_read_date = today
        message = "Starting fresh. Day 1."

    await db.commit()

    return MarkReadResponseSchema(
        message=message,
        streak=StreakResponseSchema.model_validate(streak),
    )