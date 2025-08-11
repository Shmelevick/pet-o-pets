from .base import Base
from sqlalchemy import Column, Integer, String

class Species(Base):
    """
    Вид питомца
    """
    __tablename__ = 'species'

    species_id = Column(Integer, primary_key=True)
    species_name = Column(String(30), nullable=False, comment="Вид животного")

    __table_args__ = ({'extend_existing': True})      

    def __repr__(self) -> str:
        return f"Species(species_id={self.species_id}, species_name='{self.species_name}')"  