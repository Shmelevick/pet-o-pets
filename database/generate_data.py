from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from .engine import get_engine
from models_core.base import Base
from models_core.species import Species
from models_core.m import Manipulation
from models_core.owners import Owners
from models_core.pets import Pets

from sqlalchemy import select, exists

import random
from faker import Faker
from icecream import ic

engine = get_engine()
Base.metadata.create_all(bind=engine)

SPECIES_TYPES: list = ['Собака', 'Кошка', 'Попугай', 'Хомяк', 'Черепаха', 'Кролик', 'Змея']


def _trancate_table(table_name: str) -> None:
    tables = Base.metadata.tables
    ic(table_name, tables)
    if table_name not in tables:
        raise ValueError('Unknown table name')
    print(table_name in tables)

    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))


def generate_species() -> None:
    """Генерация видов животных"""
    _trancate_table("species")
    
    
    data: list[dict[str, str]] = [{'species_name': name} for name in SPECIES_TYPES]

    engine = get_engine()
    # begin() — откроет транзакцию и закоммитит автоматически при выходе
    with engine.begin() as conn:
        conn.execute(insert(Species), data)

def generate_m() -> None:
    """Генерация манипуляций/услуг"""
    _trancate_table("m")

    columns = ['manipulation_name', 'category',  'price', 'price_min',
                'price_max', 'price_unit', 'is_range']

    m = [
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
        for row in m:
            dictionary = dict(zip(columns, row))
            print(dictionary)
            session.execute(insert(Manipulation), dictionary)

        session.commit()



def generate_owners(n=10):    # Можно добавить вывод получившихся пользователей экземплярами
    """Генерация владельцев"""
    _trancate_table("owners")

    engine = get_engine()
    fake = Faker('ru_RU')

    data = [
        {
            'owner_name': fake.name(),
            'phone': fake.phone_number(),
            'email': fake.email() if random.random() > 0.3 else None
        }
        for _ in range(n)
    ]

    with engine.begin() as conn:
        names = [row['owner_name'] for row in data]
        stmt = select(Owners.owner_name).where(Owners.owner_name.in_(names))
        existing = {row[0] for row in conn.execute(stmt).scalars()}

        new_data = [row for row in data if row['owner_name'] not in existing]

        if new_data:
            conn.execute(insert(Owners), new_data)


def _get_random_owner_id(owners_ids: list) -> int:
    ic(owners_ids)
    rand_index = random.randint(0, len(owners_ids) - 1)
    owners_id = owners_ids.pop(rand_index)
    ic(owners_ids, owners_id)
    return owners_id


def generate_pets(n=10):
    """Генерация животных. Тут N pets должно быть <= N owners"""
    _trancate_table("pets")

    fake = Faker('ru-Ru')

    with engine.begin() as conn:
        owners_ids = list(conn.execute(select(Owners.__table__.c.owner_id)).scalars())
        species_ids = conn.execute(select(Species.species_id)).scalars().all()
        ic(Owners.__table__, owners_ids, species_ids)

    data = [
        {
            "species_id": random.choice(species_ids),
            "owner_id": _get_random_owner_id(owners_ids),
            "name": fake.first_name(),
            "sex": random.choice(("M", "F")),
            "weight": random.randint(1, 30),
            "birthdate": (
                fake.date_between(start_date='-15y', end_date='-1y')
                if random.random() > 0.2 else None
            )
        }
        for _ in range(n)
    ]

    with engine.begin() as conn:
        conn.execute(insert(Pets), data)


def generate_manipulation_facts(n=20):
    _trancate_table("manipulation_facts")

    fake = Faker("ru_Ru")

    with engine.begin() as conn:
        pets_ids = list(conn.execute(select(Pets.__table__.c.id)).scalars())
        m_data = conn.execute(
            select(
                Manipulation.__table__.c.manipulation_id,
                Manipulation.__table__.c.price,
                Manipulation.__table__.c.price_min,
                Manipulation.__table__.c.price_max,
                Manipulation.__table__.c.price_unit,
                Manipulation.__table__.c.is_range
            )
        ).all()

    ic(m_data)
    l = len(m_data)
        
    data = [
        {
            "pet_id":  random.choice(pets_ids),
            "manipulation_id":  None,
            "is_planned":  None,
            "begin_time":  None,
            "end_time":  None,
            "actual_price":  _get_price(),
            "status":  None,
            "result":  None,
            "complications":  None,
            "notes":  None,
        } for _ in range(n)
    ]
    ic(data)
        



generate_species()
generate_m()
generate_owners()
generate_pets()
generate_manipulation_facts()