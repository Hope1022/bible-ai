from database.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
class UserProfile(Base):
    __tablename__= "profile"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    full_name = Column(
        String(100),
        nullable=False,
    )
    avatar_url = Column(
        Text,
        nullable=True,
    )
 
    preferred_translation = Column(
        String(20),
        nullable=False,
        default="NIV",
    )
    
    bio = Column(
        Text,
        nullable=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    
    user = relationship("User" , back_populates="profile")  