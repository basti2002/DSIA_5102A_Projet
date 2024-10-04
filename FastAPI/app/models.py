from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Pokemon(Base):
    __tablename__ = 'pokemon'

    numero = Column(Integer, primary_key=True)
    nom = Column(String)

class Type(Base):
    __tablename__ = 'type'

    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_nom = Column(String, unique=True)

class PokemonType(Base):
    __tablename__ = 'pokemon_type'

    numero = Column(Integer, ForeignKey('pokemon.numero'), primary_key=True)
    type_id = Column(Integer, ForeignKey('type.type_id'), primary_key=True)
