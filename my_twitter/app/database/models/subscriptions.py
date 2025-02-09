from typing import TYPE_CHECKING

from app.database.models import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

if TYPE_CHECKING:
    from app.database.models.user import User


class Subscriptions(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", "follower_id", name="user_id_follower_id"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(column="users.id"), nullable=False)
    follower_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id"), nullable=False
    )

    follower: Mapped["User"] = relationship(
        foreign_keys=[follower_id], back_populates="my_subscribers"
    )
    user: Mapped["User"] = relationship(
        foreign_keys=[user_id], back_populates="my_subscriptions"
    )

    @validates("follower_id")
    def validate_follower_id(self, _: str, value: int) -> int:
        if value == self.user.id:
            raise ValueError(
                f"You can't follow yourself. follower_id={value} user_id={self.user.id}"
            )
        return value
