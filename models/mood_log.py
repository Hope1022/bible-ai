from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database.database import Base


class MoodLog(Base):
    __tablename__ = "mood_logs"

    __table_args__ = (
        CheckConstraint("mood_score >= 1 AND mood_score <= 5", name="valid_mood_score"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    mood_score = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="mood_logs")

    def __repr__(self) -> str:
        return f"<MoodLog id={self.id} user_id={self.user_id} score={self.mood_score}>"