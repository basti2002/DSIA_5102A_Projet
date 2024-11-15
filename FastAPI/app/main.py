from fastapi import FastAPI, Depends, Request, Response, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import Pokemon, PokemonType, Type, User, UserSchema, UserPokemonTeam, Sensibilite, PokemonSensibilite
from fastapi.templating import Jinja2Templates
import matplotlib.pyplot as plt
from io import BytesIO
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from typing import List
from passlib.context import CryptContext
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
import numpy as np
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Configuration des paramètres JWT dans un lieu centralisé
JWT_SECRET_KEY = "your_secret_key"  # Assurez-vous de garder cette clé sécurisée
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 60 * 24 * 7

# Route principale pour gérer l'accueil et la vérification de l'utilisateur
from fastapi import HTTPException, Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional

# Définir le point de terminaison pour obtenir le token comme facultatif
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


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

from fastapi.responses import HTMLResponse

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    pokemon_count = db.query(Pokemon).count()
    if pokemon_count < 300:
        return templates.TemplateResponse("loading.html", {"request": request})

    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user = db.query(User).filter(User.username == payload.get("sub")).first()
            if user:
                logger.info(f"Home page accessed by {user.username}")
                return templates.TemplateResponse("home.html", {"request": request, "user": user.username})
        except JWTError as e:
            logger.error(f"Failed to decode JWT: {e}")

    logger.info("Home page accessed anonymously")
    return templates.TemplateResponse("home.html", {"request": request, "user": None})

@app.get("/api/pokemon/count")
async def get_pokemon_count(db: Session = Depends(get_db)):
    count = db.query(Pokemon).count()
    return {"count": count}


@app.get("/pokemon/type_count", response_class=HTMLResponse)
async def read_type_distribution(request: Request, limit: int = None, db: Session = Depends(get_db)):
    if limit is None:
        return RedirectResponse(url="/pokemon/type_count?limit=5", status_code=status.HTTP_303_SEE_OTHER)

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
    data = [{"type_name": name, "count": count} for name, count in type_distribution]
    return templates.TemplateResponse("type_count.html", {"request": request, "data": data, "limit": limit})


@app.get("/pokemon/view_db")
def view_db(request: Request, db: Session = Depends(get_db)):
    # Création d'une requête pour récupérer les noms, images et types des Pokémon
    all_pokemon = db.query(
        Pokemon.nom,
        Pokemon.image,
        Type.type_nom
    ).join(PokemonType, PokemonType.numero == Pokemon.numero)\
     .join(Type, PokemonType.type_id == Type.type_id)\
     .order_by(Pokemon.nom).all()

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


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.info(f"Generated token for {data['sub']} with expiry {expire}")
    return encoded_jwt


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    user = authenticate_credentials(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=False, secure=False, max_age=3600)
    return response


from fastapi import FastAPI, Depends, Request, Response, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from jose import jwt, JWTError

# Initialize the HTTPBearer once and use it directly with Depends
security = HTTPBearer()

def get_current_user(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise credentials_exception




@app.get("/users", response_model=List[UserSchema])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.get("/users/manage")
def manage_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("user_management.html", {"request": request, "users": users})


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



def authenticate_credentials(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    token = request.cookies.get('access_token')
    if token:
        db = next(get_db())
        try:
            payload = jwt.decode(token.split("Bearer ")[1], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            username = payload.get("sub")
            user = db.query(User).filter(User.username == username).first()
            if not user:
                response = RedirectResponse(url="/")
                response.delete_cookie("access_token")
                return response
            request.state.user = user
        except (JWTError, IndexError):
            response = RedirectResponse(url="/")
            response.delete_cookie("access_token")
            return response
        finally:
            db.close()
    return await call_next(request)


from fastapi.responses import JSONResponse

COOKIE_POLICY = {
    "httponly": False,
    "secure": False,
    "max_age": 3600,
}

@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_credentials(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed for username: {form_data.username}")
        return JSONResponse(status_code=400, content={"message": "Incorrect username or password"})
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"Login successful for username: {form_data.username}")
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=False, secure=False, max_age=3600)
    return response


@app.post("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

from fastapi import Form


def base64_encode(value):
    return base64.b64encode(value).decode("utf-8")

# Ajouter le filtre à l'environnement Jinja2
templates.env.filters['b64encode'] = base64_encode


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


from sqlalchemy.exc import IntegrityError

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