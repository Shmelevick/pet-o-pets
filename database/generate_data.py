from sqlalchemy import insert
from sqlalchemy.orm import Session

from .engine import get_engine

from models_core.base import Base
from models_core.species import Species
from models_core.manipulations import Manipulation


engine = get_engine()
Base.metadata.create_all(bind=engine)


def generate_species() -> None:
    """Генерация видов животных"""
    species_types: list = ['Собака', 'Кошка', 'Попугай', 'Хомяк', 'Черепаха', 'Кролик', 'Змея']
    data: list[dict[str, str]] = [{'species_name': name} for name in species_types]

    engine = get_engine()
    # begin() — откроет транзакцию и закоммитит автоматически при выходе
    with engine.begin() as conn:
        conn.execute(insert(Species), data)

def generate_manipulations() -> None:
    """Генерация манипуляций/услуг"""

    columns = ['manipulation_name', 'category',  'price', 'price_min',
                'price_max', 'price_unit', 'is_range']

    manipulations = [
        ('Консультация', 'Терапия', None, 500, 1000, '₽', True),
        ('Анализ крови', 'Диагностика', 1500, None, None, '₽', False),
        ('УЗИ', 'Диагностика', None, 2000, 3000, '₽', True),
        ('Стерилизация', 'Хирургия', None, 3000, 5000, '₽', True),
        ('Чистка зубов', 'Стоматология', 2500, None, None, '₽', False),
        ('Вакцинация', 'Вакцинация', None, 1000, 1500, '₽', True),
        ('Стрижка', 'Груминг', None, 800, 2000, '₽', True),
        ('Рентген', 'Диагностика', None, 1200, 2500, '₽', True),
        ('Кастрация', 'Хирургия', None, 2000, 4000, '₽', True),
        ('Обработка от паразитов', 'Терапия', 500, None, None, '₽', False)
    ]

    engine = get_engine()
    with Session(engine) as session:
        for row in manipulations:
            dictionary = dict(zip(columns, row))
            print(dictionary)
            session.execute(insert(Manipulation), dictionary)

        session.commit()


generate_species()
generate_manipulations()
