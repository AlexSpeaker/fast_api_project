from typing import TYPE_CHECKING

from app.database.models import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.database.models.tweet import Tweet


class Attachment(Base):
    __tablename__ = "attachments"
    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(column="tweets.id", ondelete="CASCADE"), nullable=True
    )
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    tweet: Mapped["Tweet"] = relationship(back_populates="attachments")
