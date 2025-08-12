from decimal import Decimal
from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from .engine import get_engine
from models_core.base import Base
from models_core.species import Species
from models_core.manipulations import Manipulation
from models_core.manipulation_facts import ManipulationFacts
from models_core.owners import Owners
from models_core.owners_history import OwnersHistory
from models_core.pets import Pets

from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone

import random, math
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

def generate_manipulations() -> None:
    """Генерация манипуляций/услуг"""
    _trancate_table("manipulations")

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



def generate_weighted_number(numbers:list, weights:list) -> int:    
    # Нормализуем веса (если они в сумме не дают 100)
    total = sum(weights)
    normalized_weights = [w/total for w in weights]
    
    return random.choices(numbers, weights=normalized_weights, k=1)[0]


def generate_manipulation_facts() -> None:
    """Генерация фактов о проведенных манипуляциях"""

    statuses = ['planned', 'completed', 'canceled', 'rescheduled']
    results = [
        "Успешно завершено", 
        "Требуется повторное проведение", 
        "Осложнений не было", 
        "Пациент чувствует себя хорошо",
        "Требуется наблюдение"
    ]

    fake = Faker('ru_RU')

    with Session(engine) as session:
        total_pets = session.execute(select(Pets)).fetchall()
        manipulations = session.execute(select(Manipulation)).fetchall()

        for pet in total_pets:
            if pet.Pets.birthdate:
                years = math.ceil((datetime.now(timezone.utc) - pet.Pets.birthdate).days / 365.25)
            else:
                years = 1

            visits_count = random.randint(1, 2)

            for _ in range(visits_count):
                while True:  # пока не запишется без ошибки
                    is_planned = random.random() > 0.2
                    manipulation = random.choice(manipulations)

                    if manipulation.Manipulation.is_range:
                        actual_price = Decimal(
                            random.uniform(
                                float(manipulation.Manipulation.price_min),
                                float(manipulation.Manipulation.price_max)
                            )
                        )
                    else:
                        actual_price = manipulation.Manipulation.price

                    if random.random() > 0.7:
                        actual_price *= Decimal(random.uniform(0.8, 1.2))   

                    actual_price = round(actual_price, 2)
                    
                    weights = [0.2, 0.6, 0.1, 0.1]
                    status = generate_weighted_number(statuses, weights)

                    begin_time = fake.date_time_between(start_date='-1y', end_date='now')
                    end_time = (begin_time + timedelta(minutes=random.randint(5, 180))
                                if status == 'completed' else None)

                    fact = ManipulationFacts(
                        pet_id=pet.Pets.id,
                        manipulation_id=manipulation.Manipulation.manipulation_id,
                        is_planned=is_planned,
                        begin_time=begin_time,
                        end_time=end_time,
                        actual_price=actual_price,
                        status=status,
                        result=random.choice(results) if status == 'completed' else None,
                        complications=fake.text() if random.random() > 0.8 else None,
                        notes=fake.text() if random.random() > 0.7 else None
                    )

                    try:
                        session.add(fact)
                        session.commit()
                        break
                    except Exception as e:
                        print('generate_manipulation_facts error', e)
                        print(pet)
                        session.rollback()
                        continue


def generate_owners_history() -> None:
    """Генерация истории владельцев"""
    with Session(engine) as session:
        pet_ids = [id[0] for id in session.execute(select(Pets.id)).fetchall()]
        owner_ids = [id[0] for id in session.execute(select(Owners.owner_id)).fetchall()]   
         
    fake = Faker('ru_RU')    
    data = []

    for pet_id in pet_ids:
        # У каждого питомца может быть от 1 до 3-х владельцев в истории владельцев
        num_owners = random.randint(1, 3)
        owners = random.sample(owner_ids, num_owners)
        
        start_date = fake.date_time_between(start_date='-5y', end_date='-1y')
        for i, owner_id in enumerate(owners):
            if i == len(owners) - 1:
                # Текущий владелец - end_date = None
                data.append({
                    'pet_id': pet_id,
                    'owner_id': owner_id,
                    'start_date': start_date,
                    'end_date': None
                })
            else:
                # Бывший владелец - имеет end_date
                end_date = start_date + timedelta(days=random.randint(30, 365))
                data.append({
                    'pet_id': pet_id,
                    'owner_id': owner_id,
                    'start_date': start_date,
                    'end_date': end_date
                })
                start_date = end_date + timedelta(days=random.randint(1, 30))
    with Session(engine) as session:
        session.execute(insert(OwnersHistory), data)
        session.commit() 


generate_species()
generate_manipulations()
generate_owners()
generate_pets()
generate_manipulation_facts()
generate_owners_history()
