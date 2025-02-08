from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
