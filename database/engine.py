import os

from icecream import ic
from dotenv import load_dotenv

from models_core.base import Base

from sqlalchemy import create_engine


load_dotenv('.env')

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")


def get_engine():
    try:
        ic(user, password, db, host, port)
        engine = create_engine(
            f"postgresql://{user}:{password}@{host}:{port}/{db}",
            echo=True
        )
        Base.metadata.create_all(engine)
        return engine
    
    except Exception as e:
        print('Error!', e)
