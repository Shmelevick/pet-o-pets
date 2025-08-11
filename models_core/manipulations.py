from .base import Base
from sqlalchemy import Column, Integer, String, Numeric, Boolean, CheckConstraint

class Manipulation(Base):
    """
    Тип манипуляции, производимой с питомцем
    с расширенными полями для хранения прайс-листа
    """

    __tablename__ = 'manipulations'

    manipulation_id = Column(Integer, primary_key=True, autoincrement=True)
    manipulation_name = Column(String(100), nullable=False, comment="Название манипуляции")
    category = Column(String(50), nullable=True, comment="Терапия, Хирургия и т.д.")
    price = Column(Numeric(10, 2), nullable=True, comment="Основная цена")
    price_min = Column(Numeric(10, 2), nullable=True, comment="Для диапазона от X")
    price_max = Column(Numeric(10, 2), nullable=True, comment="Для диапазона до Y")
    price_unit = Column(String(10), default='₽', comment="Валюта")
    is_range = Column(Boolean, default=False, comment="Флаг диапазона цен")

    __table_args__ = (
        CheckConstraint("price IS NULL OR price >= 0", name="chk_price_nonneg"),
        CheckConstraint("price_min IS NULL OR price_min >= 0", name="chk_price_min_nonneg"),
        CheckConstraint("price_max IS NULL OR price_max >= 0", name="chk_price_max_nonneg"),
        CheckConstraint(
            "(price_min IS NULL OR price_max IS NULL) OR (price_min <= price_max)",
            name="chk_price_bounds",
        ),
        {"comment": "Справочник манипуляций с ценами"},
    )

    def __repr__(self):
        if self.is_range:
            return f"<Manipulation {self.manipulation_name} (от {self.price_min} до {self.price_max} {self.price_unit})>"
        else:
            return f"<Manipulation {self.manipulation_name} ({self.price} {self.price_unit})>"
