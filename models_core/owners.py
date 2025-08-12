from __future__ import annotations

from sqlalchemy import Integer, String, CheckConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from models_core.base import Base


class Owners(Base):
    """
    Владельцы питомцев
    """
    __tablename__ = "owners"

    owner_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True,
        comment="ID владельца"
    )

    owner_name: Mapped[str] = mapped_column(
        String(100), nullable=False,
        comment="Полное имя владельца"
    )

    phone: Mapped[str | None] = mapped_column(
        String(32), nullable=True,
        comment="Номер телефона в международном формате"
    )

    email: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Адрес электронной почты"
    )

    __table_args__ = (
        CheckConstraint("length(owner_name) > 0", name="chk_owner_name_nonempty"),
        {"comment": "Справочник владельцев питомцев"},
    )

    def __repr__(self) -> str:
        return (
            f"Owners(owner_id={self.owner_id}, owner_name='{self.owner_name}', "
            f"phone='{self.phone}', email='{self.email}')"
        )
