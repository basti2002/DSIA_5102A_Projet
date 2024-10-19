from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone, timedelta

class Pokemon(Base):
    __tablename__ = 'pokemon'
    numero = Column(Integer, primary_key=True)
    nom = Column(String)
    image = Column(String)
    types = relationship("Type", secondary="pokemon_type", back_populates="pokemons")

class Type(Base):
    __tablename__ = 'type'
    type_id = Column(Integer, primary_key=True)
    type_nom = Column(String, unique=True)
    pokemons = relationship("Pokemon", secondary="pokemon_type", back_populates="types")


class PokemonType(Base):
    __tablename__ = 'pokemon_type'
    numero = Column(Integer, ForeignKey('pokemon.numero'), primary_key=True)
    type_id = Column(Integer, ForeignKey('type.type_id'), primary_key=True)
    
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    user = relationship("User", back_populates="posts")

class UserSchema(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


