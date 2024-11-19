from sqlalchemy import Column, Integer,Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint
from database import Base
from datetime import datetime
from pydantic import BaseModel

# Représente un Pokémon avec ses caractéristiques et relations
class Pokemon(Base):
    __tablename__ = 'pokemon'
    numero = Column(Integer, primary_key=True)
    nom = Column(String)
    image_mini = Column(String)
    lien = Column(String)
    image = Column(String)
    types = relationship("Type", secondary="pokemon_type", back_populates="pokemons") # Types associés via table de liaison
    sensibilites = relationship("PokemonSensibilite", back_populates="pokemon") # Représente un Pokémon avec ses détails et relations

# Détaille les types de Pokémon comme Feu ou Eau
class Type(Base):
    __tablename__ = 'type'
    type_id = Column(Integer, primary_key=True)
    type_nom = Column(String, unique=True)
    pokemons = relationship("Pokemon", secondary="pokemon_type", back_populates="types") # Pokémons associés à ce type

# Table de liaison entre Pokémon et leurs types pour gérer la relation many-to-many
class PokemonType(Base):
    __tablename__ = 'pokemon_type'
    numero = Column(Integer, ForeignKey('pokemon.numero'), primary_key=True)
    type_id = Column(Integer, ForeignKey('type.type_id'), primary_key=True)

# Détaille les valeurs de sensibilité des Pokémon face à différents types
class Sensibilite(Base):
    __tablename__ = 'sensibilite'
    sensibilite_id = Column(Integer, primary_key=True)
    valeur = Column(Float, unique=True)

# Associe les Pokémon à des sensibilités spécifiques et les relie aux types concernés
class PokemonSensibilite(Base):
    __tablename__ = 'pokemon_sensibilite'
    numero = Column(Integer, ForeignKey('pokemon.numero'), primary_key=True)
    type_id = Column(Integer, ForeignKey('type.type_id'), primary_key=True)
    sensibilite_id = Column(Integer, ForeignKey('sensibilite.sensibilite_id'), primary_key=True)
    pokemon = relationship("Pokemon", back_populates="sensibilites")
    type = relationship("Type")
    sensibilite = relationship("Sensibilite")


# Utilisateur avec ses Pokémon (son équipe) et ses posts
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True) # Identifiant unique de l'utilisateur
    username = Column(String, unique=True) # Nom d'utilisateur unique
    hashed_password = Column(String) # Mot de passe crypté
    posts = relationship("Post", back_populates="user")
    pokemon_team = relationship("UserPokemonTeam", back_populates="user") # Équipe de Pokémon de l'utilisateur

    # Vérifie si l'équipe de l'utilisateur a de la place pour un nouveau Pokémon
    def has_space_in_team(self):
        return len(self.pokemon_team) < 6

# Gère l'équipe de Pokémon de chaque utilisateur, limitée à 6
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

# Représente un post créé par un utilisateur
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True) # Identifiant unique du post
    user_id = Column(Integer, ForeignKey('users.id')) # Utilisateur qui a créé le post
    title = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc)) # Date de création du post
    user = relationship('User', back_populates='posts') # Lien vers l'utilisateur créateur du post

# Schéma pour la sérialisation des données utilisateur, utilisé par Pydantic
class UserSchema(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True # Permet la compatibilité avec les objets ORM de SQLAlchemy