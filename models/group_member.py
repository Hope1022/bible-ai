import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from database.database import Base


class GroupMemberRole(str, enum.Enum):
    leader = "leader"
    member = "member"


class GroupMember(Base):
    __tablename__ = "group_members"

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="unique_group_member"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    group_id = Column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(
        Enum(GroupMemberRole),
        nullable=False,
        default=GroupMemberRole.member,
    )

    joined_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_members")

    def __repr__(self) -> str:
        return f"<GroupMember group_id={self.group_id} user_id={self.user_id} role={self.role}>"