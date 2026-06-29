from database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime,Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

class UserRole(str, enum.Enum):
    
    member = "member"   # regular user — most people
    pastor = "pastor"   # church leader — can manage a church group
    admin  = "admin"    # us (the developers) — full access
 
class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True,nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    google_id = Column(
        String(255),
        unique=True,
        nullable=True,
    )
    role = Column(Enum(UserRole), nullable=False,default=UserRole.member)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    streak      = relationship("Streak", back_populates="user", uselist=False)
    journals    = relationship("Journal", back_populates="user")
    # prayers     = relationship("Prayer", back_populates="user")
    groups      = relationship("GroupMember", back_populates="user")
    profile     = relationship("UserProfile", back_populates="user", uselist=False)#one to one relationship for uselist=false means
    sessions    = relationship("Session", back_populates="user")
    mood_logs = relationship("MoodLog", back_populates="user")
    group_members = relationship("GroupMember", back_populates="user")
    messages = relationship("Message", back_populates="user")
def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"