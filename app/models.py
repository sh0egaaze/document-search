from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"Document(id={self.id}, created_date={self.created_date})"