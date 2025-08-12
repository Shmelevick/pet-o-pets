from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, DateTime, ForeignKey,
    CheckConstraint, text
)
from sqlalchemy.orm import Mapped, mapped_column

from models_core.base import Base


class Pets(Base):
    """
    Справочник питомцев
    """
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True,comment="ID питомца")

    species_id: Mapped[int | None] = mapped_column(
        ForeignKey("species.species_id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="ID вида животного")

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("owners.owner_id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="ID владельца")

    name: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Кличка питомца")

    sex: Mapped[str] = mapped_column(
        String(1), nullable=False,
        server_default=text("'M'"),
        comment="Пол: M — мужской, F — женский")

    weight: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Вес в кг")

    birthdate: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Дата рождения")

    __table_args__ = (
        # Допустимые значения пола
        CheckConstraint(
            "sex IN ('M', 'F')",
            name="chk_pet_sex_valid"
        ),
        # Вес не может быть отрицательным
        CheckConstraint(
            "weight IS NULL OR weight >= 0",
            name="chk_pet_weight_nonneg"
        ),
        {"comment": "Справочник питомцев"})

    def __repr__(self) -> str:
        return (
            f"Pets(id={self.id}, species_id={self.species_id}, owner_id={self.owner_id}, "
            f"name='{self.name}', sex='{self.sex}', weight={self.weight}, birthdate='{self.birthdate}')"
        )
