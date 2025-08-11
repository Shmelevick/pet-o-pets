from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric,
    CheckConstraint, Index, func, text
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ManipulationFacts(Base):
    """
    Факты о проведённых манипуляциях с животными
    """
    __tablename__ = "manipulation_facts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    pet_id: Mapped[int] = mapped_column(
        ForeignKey("pets.id", ondelete="CASCADE"),
        index=True, nullable=False, comment="id питомца"
    )

    manipulation_id: Mapped[int] = mapped_column(
        ForeignKey("manipulations.manipulation_id", ondelete="RESTRICT"),
        index=True, nullable=False, comment="id манипуляции"
    )

    is_planned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"),
        comment="Запланированная (true) или экстренная (false)"
    )

    begin_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        comment="Время начала"
    )

    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Время окончания"
    )

    actual_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True,
        comment="Фактическая стоимость с учетом корректировок"
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'planned'"),
        comment="Статус: planned/completed/canceled/rescheduled"
    )

    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    complications: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Описание осложнений")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Доп. заметки")

    __table_args__ = (
        # --- валидность значений ---
        CheckConstraint("actual_price IS NULL OR actual_price >= 0", name="chk_fact_price_nonneg"),
        CheckConstraint(
            "end_time IS NULL OR end_time >= begin_time",
            name="chk_fact_end_after_begin"
        ),
        # допустимые статусы
        CheckConstraint(
            "status IN ('planned','completed','canceled','rescheduled')",
            name="chk_fact_status_allowed"
        ),
        # если статус completed — должно быть end_time
        CheckConstraint(
            "(status <> 'completed') OR (end_time IS NOT NULL)",
            name="chk_fact_completed_has_end"
        ),

        # --- индексы ---
        Index("ix_mf_pet_begin_time", "pet_id", "begin_time"),
        Index("ix_mf_status_begin_time", "status", "begin_time"),

        # комментарий к таблице
        {"comment": "Факты о манипуляциях (история процедур)"},
    )

    def duration(self) -> float | None:
        """Продолжительность процедуры в минутах."""
        if self.end_time:
            return (self.end_time - self.begin_time).total_seconds() / 60
        return None
