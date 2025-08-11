from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Integer, DateTime, ForeignKey, CheckConstraint, Index, text
)
from sqlalchemy.orm import Mapped, mapped_column
from models_core.base import Base


class OwnersHistory(Base):
    """
    Исторические данные о владельцах питомцев
    """
    __tablename__ = "owners_history"

    record_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    pet_id: Mapped[int] = mapped_column(
        ForeignKey("pets.id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="id животного"
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("owners.owner_id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="id владельца"
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        comment="первая дата обращения владельца с этим животным"
    )

    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="последняя дата владения животным"
    )

    __table_args__ = (
        # end_date >= start_date, если обе даты заданы
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="chk_owners_history_date_order"
        ),
        Index("ix_oh_pet_id_start_date", "pet_id", "start_date"),
        {"comment": "История владения питомцами"},
    )

    def __repr__(self) -> str:
        return (
            f"OwnersHistory(record_id={self.record_id}, pet_id={self.pet_id}, "
            f"owner_id={self.owner_id}, start_date='{self.start_date}', end_date='{self.end_date}')"
        )
