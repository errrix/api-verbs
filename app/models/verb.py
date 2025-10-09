from datetime import datetime
from typing import List

from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Verb(Base):
    """Модель глагола (инфинитив)"""
    __tablename__ = "verbs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    infinitive: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationship
    forms: Mapped[List["VerbForm"]] = relationship("VerbForm", back_populates="verb", cascade="all, delete-orphan")


class VerbForm(Base):
    """Модель формы глагола"""
    __tablename__ = "verb_forms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    verb_id: Mapped[int] = mapped_column(ForeignKey("verbs.id", ondelete="CASCADE"), index=True)
    tense: Mapped[str] = mapped_column(String(100), index=True)
    person: Mapped[str] = mapped_column(String(10))
    auxiliary_verb: Mapped[str | None] = mapped_column(String(50), nullable=True)
    verb_form: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationship
    verb: Mapped["Verb"] = relationship("Verb", back_populates="forms")

