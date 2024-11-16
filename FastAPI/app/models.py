from sqlalchemy import Column, Integer,Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint
from database import Base
from datetime import datetime
from pydantic import BaseModel

class Pokemon(Base):
    __tablename__ = 'pokemon'
    numero = Column(Integer, primary_key=True)
    nom = Column(String)
    image_mini = Column(String)
    lien = Column(String)
    image = Column(String)
    types = relationship("Type", secondary="pokemon_type", back_populates="pokemons")
    sensibilites = relationship("PokemonSensibilite", back_populates="pokemon")

class Type(Base):
    __tablename__ = 'type'
    type_id = Column(Integer, primary_key=True)
    type_nom = Column(String, unique=True)
    pokemons = relationship("Pokemon", secondary="pokemon_type", back_populates="types")

class PokemonType(Base):
    __tablename__ = 'pokemon_type'
    numero = Column(Integer, ForeignKey('pokemon.numero'), primary_key=True)
    type_id = Column(Integer, ForeignKey('type.type_id'), primary_key=True)

class Sensibilite(Base):
    __tablename__ = 'sensibilite'
    sensibilite_id = Column(Integer, primary_key=True)
    valeur = Column(Float, unique=True)

class PokemonSensibilite(Base):
    __tablename__ = 'pokemon_sensibilite'
    numero = Column(Integer, ForeignKey('pokemon.numero'), primary_key=True)
    type_id = Column(Integer, ForeignKey('type.type_id'), primary_key=True)
    sensibilite_id = Column(Integer, ForeignKey('sensibilite.sensibilite_id'), primary_key=True)
    # Relations
    pokemon = relationship("Pokemon", back_populates="sensibilites")
    type = relationship("Type")
    sensibilite = relationship("Sensibilite")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    posts = relationship("Post", back_populates="user")
    pokemon_team = relationship("UserPokemonTeam", back_populates="user")

    def has_space_in_team(self):
        return len(self.pokemon_team) < 6

class UserPokemonTeam(Base):
    __tablename__ = 'user_pokemon_team'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    pokemon_id = Column(Integer, ForeignKey('pokemon.numero'))
    slot = Column(Integer, primary_key=True)
    user = relationship("User", back_populates="pokemon_team")
    pokemon = relationship("Pokemon")

    __table_args__ = (
        CheckConstraint('slot >= 0 AND slot <= 6', name='slot_range'),
    )

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    # Lien retour vers User
    user = relationship('User', back_populates='posts')

class UserSchema(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True