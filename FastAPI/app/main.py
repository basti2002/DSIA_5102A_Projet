from fastapi import FastAPI, Depends, Request, Response, status, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import  RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
import matplotlib.pyplot as plt
import numpy as np
import logging
import base64
from io import BytesIO
from database import SessionLocal
from models import Pokemon, PokemonType, Type, User, UserSchema, UserPokemonTeam

# Configuration de la sécurité des mots de passe avec CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialisation de FastAPI
app = FastAPI()

# Configuration pour servir des fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration du système de templates Jinja2 pour la génération de réponses HTML
templates = Jinja2Templates(directory="templates")

# Configuration de base du système de logging pour le suivi des activités de l'application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Générateur de session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuration des paramètres pour l'authentification par JWT
JWT_SECRET_KEY = "your_secret_key"  
JWT_ALGORITHM = "HS256"            
JWT_EXPIRATION_TIME_MINUTES = 60 * 24 * 7

# Configuration de l'authentification OAuth2 pour la récupération facultative des tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Configuration de l'authentification HTTP basée sur les cookies
security = HTTPBearer()

# Gestion des cookies utilisée lors de la gestion des sessions utilisateur
COOKIE_POLICY = {
    "httponly": False,
    "secure": False,    
    "max_age": 3600     
}



# Vérification de l'existence de l'utilisateur
def check_user_exists(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()

# Vérification que l'utilisateur est connecté via un token valide
def check_user_logged_in(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("sub"):
            logger.info(f"Token valid for user {payload.get('sub')}")
            return True
        return False
    except JWTError as e:
        logger.error(f"Token validation error: {str(e)}")
        return False

# Gestion de la page d'accueil
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    pokemon_count = db.query(Pokemon).count() # Compter le nombre de Pokemons
    if pokemon_count < 300: # Si moins de 300 Pokemons, afficher la page de chargement
        return templates.TemplateResponse("loading.html", {"request": request})

    if token: # Si un token est fourni, verifier si l'utilisateur est connecté
        try: # Vérifier si le token est valide
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user = db.query(User).filter(User.username == payload.get("sub")).first()
            if user: # Si l'utilisateur est trouvé, afficher la page d'accueil sur laquelle il est connecté
                logger.info(f"Home page accessed by {user.username}")
                return templates.TemplateResponse("home.html", {"request": request, "user": user.username})
        except JWTError as e: # Si le token n'est pas valide pas de connexion
            logger.error(f"Failed to decode JWT: {e}")

    logger.info("Home page accessed anonymously") # Si le token est invalide, afficher la page d'accueil anonyme
    return templates.TemplateResponse("home.html", {"request": request, "user": None})

# Récupérer le nombre total de Pokemons, utilisé pour la page de chargement
@app.get("/api/pokemon/count")
async def get_pokemon_count(db: Session = Depends(get_db)):
    count = db.query(Pokemon).count()
    return {"count": count}

# Récupérer la distribution des types de Pokemons
@app.get("/pokemon/type_count", response_class=HTMLResponse)
async def read_type_distribution(request: Request, limit: int = None, db: Session = Depends(get_db)):
    if limit is None: # Si aucun limit n'est fourni, utiliser 5 par défaut
        return RedirectResponse(url="/pokemon/type_count?limit=5", status_code=status.HTTP_303_SEE_OTHER)

    # Récupérer la distribution des types de Pokemons par ordre décroissant (plus d'occurence en premier)
    type_distribution = (
        db.query(
            Type.type_nom,
            func.count(PokemonType.numero).label('count')
        )
        .join(PokemonType, PokemonType.type_id == Type.type_id)
        .group_by(Type.type_nom)
        .order_by(func.count(PokemonType.numero).desc())
        .limit(limit)
        .all()
    )
    # Créer une liste de dictionnaires pour l'affichage sur la page HTML avec le nom du type et le nombre de Pokémon 
    data = [{"type_name": name, "count": count} for name, count in type_distribution]
    return templates.TemplateResponse("type_count.html", {"request": request, "data": data, "limit": limit})


# Récupérer la liste des Pokemons avec leurs types leur nom et leur image pour afficher tout les pokemons disponibles
@app.get("/pokemon/view_db")
def view_db(request: Request, db: Session = Depends(get_db)):
    # Création d'une requête pour récupérer les noms, images et types des Pokémon
    all_pokemon = db.query(
        Pokemon.nom,
        Pokemon.image,
        Type.type_nom
    ).join(PokemonType, PokemonType.numero == Pokemon.numero)\
     .join(Type, PokemonType.type_id == Type.type_id)\
     .order_by(Pokemon.nom).all() # Trier les Pokémon par ordre alphabétique

    # Dictionnaire pour accumuler les données des Pokémon
    pokemon_data = {}
    for nom, image, type_nom in all_pokemon:
        if nom not in pokemon_data:
            pokemon_data[nom] = {"nom": nom, "image": image, "types": [type_nom]}
        else:
            pokemon_data[nom]["types"].append(type_nom)

    # Conversion du dictionnaire en liste pour l'affichage
    pokemon_list = list(pokemon_data.values())
    
    return templates.TemplateResponse("view_db.html", {
        "request": request,
        "pokemon_data": pokemon_list
    })

# Créer un token JWT pour l'utilisateur connecté
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.info(f"Generated token for {data['sub']} with expiry {expire}")
    return encoded_jwt

# Récupérer l'utilisateur actuellement connecté
def get_current_user(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials") # Si le token n'est pas valide, renvoyer une erreur
    try: # Vérifier si le token est valide
        # Décoder le JWT pour extraire l'ID utilisateur
        payload = jwt.decode(token.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id") # Récupérer l'ID utilisateur
        if user_id is None: # Si l'utilisateur n'est pas trouvé, renvoyer une erreur
            raise credentials_exception 
        user = db.query(User).filter(User.id == user_id).first() # Récuperer l'utilisateur correspondant à l'ID
        if user is None: # Si cet user n'existe pas dans la base de données, renvoyer une erreur
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise credentials_exception

# Récupérer tous les utilisateurs
@app.get("/users", response_model=List[UserSchema])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Gestion des utilisateurs
@app.get("/users/manage")
def manage_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("user_management.html", {"request": request, "users": users}) # Afficher la page de gestion des utilisateurs avec la liste des utilisateurs

# Créer un nouvel utilisateur
@app.post("/users/create")
async def create_user(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        users = db.query(User).all()  # Récupérer tous les utilisateurs pour les lister sur la page
        return templates.TemplateResponse("user_management.html", {
            "request": request,
            "users": users,
            "error": "Username already taken"
        })

    # Hasher le mot de passe
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()

    # Rediriger vers la gestion des utilisateurs après la création
    return RedirectResponse(url=request.url_for("manage_users"), status_code=status.HTTP_302_FOUND)


# Authentifier l'utilisateur et créer un token JWT
def authenticate_credentials(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

# Middleware pour authentifier l'utilisateur
@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    token = request.cookies.get('access_token') # Récupérer le token depuis les cookies
    if token: # Si un token est fourni
        db = next(get_db()) # Récupérer la session de base de données
        try: # Vérifier si le token est valide et si l'utilisateur existe
            payload = jwt.decode(token.split("Bearer ")[1], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]) # Décoder le JWT pour extraire l'ID utilisateur
            username = payload.get("sub")
            user = db.query(User).filter(User.username == username).first()
            if not user: # Si l'utilisateur n'existe pas, renvoyer une erreur
                response = RedirectResponse(url="/")
                response.delete_cookie("access_token")
                return response
            request.state.user = user
        except (JWTError, IndexError): # Si le token est invalide, renvoyer une erreur
            response = RedirectResponse(url="/")
            response.delete_cookie("access_token")
            return response
        finally: # Fermer la session de base de données
            db.close()
    return await call_next(request) 


# Authentication de l'utilisateur
@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_credentials(db, form_data.username, form_data.password) # Authentifier l'utilisateur
    if not user: # Si l'utilisateur n'existe pas
        logger.warning(f"Login failed for username: {form_data.username}") # Enregistrer l'erreur
        return templates.TemplateResponse("home.html", { # Afficher la page d'accueil avec un message d'erreur
            "request": request,
            "error": "Identifiant ou mot de passe incorrect"
        })
    access_token = create_access_token(data={"sub": user.username}) # Créer un token JWT
    logger.info(f"Login successful for username: {form_data.username}")
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=False, secure=False, max_age=3600) # Enregistrer le token JWT dans un cookie
    return response


# Deconnexion de l'utilisateur
@app.post("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token") # Effacer le token JWT issu du cookie du navigateur
    return response

# Gestion du favicon
@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

# Filtre pour encoder une valeur en base64
def base64_encode(value):
    return base64.b64encode(value).decode("utf-8")

# Ajouter le filtre à l'environnement Jinja2
templates.env.filters['b64encode'] = base64_encode

# Afficher l'équipe de Pokémon
@app.get("/equipe_pokemon", response_class=HTMLResponse)
async def equipe_pokemon(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if user:
        # Récupérer l'équipe de Pokémon de l'utilisateur
        team = db.query(UserPokemonTeam).filter(UserPokemonTeam.user_id == user.id).join(Pokemon, UserPokemonTeam.pokemon_id == Pokemon.numero).all()

        if not team:
            logger.info(f"Aucune équipe trouvée pour l'utilisateur {user.id}, équipe vide.")
            team = []

        # Calculer les sensibilités agrégées pour chaque type
        type_sensibility_totals = {}
        for member in team:
            for sensibilite in member.pokemon.sensibilites:
                type_nom = sensibilite.type.type_nom
                valeur = sensibilite.sensibilite.valeur
                type_sensibility_totals[type_nom] = type_sensibility_totals.get(type_nom, 0) + valeur

        # Organiser les données pour le graphique
        types = list(type_sensibility_totals.keys())
        valeurs = list(type_sensibility_totals.values())

        # Trouver les 2 points faibles et les 2 points forts
        sorted_indices = np.argsort(valeurs)
        points_faibles = sorted_indices[-2:]
        points_forts = sorted_indices[:2]

        # Créer le diagramme en étoile
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        angles = np.linspace(0, 2 * np.pi, len(types), endpoint=False).tolist()
        valeurs += valeurs[:1]  # Boucler le graphique
        angles += angles[:1]

        ax.fill(angles, valeurs, color='#FFA07A', alpha=0.25)
        ax.plot(angles, valeurs, color='#FFA07A', linewidth=2)

        # Colorer les points forts et faibles
        for i in points_faibles:
            ax.plot([angles[i], angles[i]], [0, valeurs[i]], color='red', linewidth=3)
        for i in points_forts:
            ax.plot([angles[i], angles[i]], [0, valeurs[i]], color='green', linewidth=3)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(types)

        # Sauvegarder le diagramme dans un buffer pour l'afficher dans le template
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        img_data = buf.getvalue()

        # Passer les données à TemplateResponse pour le rendu HTML
        return templates.TemplateResponse("equipe_pokemon.html", {
            "request": request,
            "user": user, 
            "all_pokemon": db.query(Pokemon).all(),
            "team": team,
            "radar_chart": img_data
        })
    else:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")



@app.post("/equipe_pokemon")
async def update_team(
    request: Request, 
    db: Session = Depends(get_db), 
    pokemon_id: int = Form(...), 
    user_id: int = Form(...), 
    slot_number: int = Form(...), 
    action: str = Form(...)
):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    try:
        if action == "Ajouter":
            team_size = db.query(UserPokemonTeam).filter(
                UserPokemonTeam.user_id == user.id,
                UserPokemonTeam.pokemon_id.isnot(None)
            ).count()

            if team_size >= 6:
                raise HTTPException(status_code=400, detail="L'équipe est déjà pleine.")

            slot = db.query(UserPokemonTeam).filter(
                UserPokemonTeam.user_id == user.id,
                UserPokemonTeam.slot == slot_number
            ).first()

            if slot and slot.pokemon_id is None:
                slot.pokemon_id = pokemon_id
            elif not slot:
                new_slot = UserPokemonTeam(user_id=user.id, slot=slot_number, pokemon_id=pokemon_id)
                db.add(new_slot)
            else:
                raise HTTPException(status_code=400, detail="Slot non disponible ou déjà rempli.")

            db.commit()

        elif action == "Retirer":
            pokemon_to_remove = db.query(UserPokemonTeam).filter(
                UserPokemonTeam.user_id == user.id,
                UserPokemonTeam.pokemon_id == pokemon_id,
                UserPokemonTeam.slot == slot_number
            ).first()

            if pokemon_to_remove:
                db.delete(pokemon_to_remove)
                db.commit()

                remaining_team = db.query(UserPokemonTeam).filter(
                    UserPokemonTeam.user_id == user.id
                ).order_by(UserPokemonTeam.slot).all()

                for i, team_member in enumerate(remaining_team, start=1):
                    team_member.slot = i

                db.commit()

            else:
                raise HTTPException(status_code=400, detail="Pokémon non trouvé dans le slot spécifié.")

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse(url="/equipe_pokemon", status_code=status.HTTP_303_SEE_OTHER)