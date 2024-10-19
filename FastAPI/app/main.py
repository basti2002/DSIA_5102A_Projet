from fastapi import FastAPI, Depends, Request, Response, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import Pokemon, PokemonType, Type, User, UserSchema
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=Response)
def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/pokemon/type_count", response_class=Response)
def read_type_distribution(db: Session = Depends(get_db)):
    type_distribution = db.query(
        Type.type_nom, func.count(PokemonType.numero).label('count')
    ).join(Type, PokemonType.type_id == Type.type_id)\
     .group_by(Type.type_nom).all()

    # Data for plotting
    type_names = [type_name for type_name, _ in type_distribution]
    counts = [count for _, count in type_distribution]

    # Create a plot
    fig, ax = plt.subplots()
    ax.bar(type_names, counts, color='skyblue')
    ax.set_xlabel('Types de Pokémon')
    ax.set_ylabel('Nombre de Pokémon')
    ax.set_title('Distribution des Pokémon par Type')
    plt.xticks(rotation=45)

    # Save plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")

@app.get("/pokemon/view_db")
def view_db(request: Request, db: Session = Depends(get_db)):
    all_pokemon = db.query(
        Pokemon.nom,
        Pokemon.image,
        Type.type_nom
    ).select_from(Pokemon)\
     .join(PokemonType, PokemonType.numero == Pokemon.numero)\
     .join(Type, PokemonType.type_id == Type.type_id)\
     .order_by(Pokemon.nom).all()

    pokemon_data = []
    for pokemon in all_pokemon:
        if not any(p['nom'] == pokemon.nom for p in pokemon_data):
            pokemon_data.append({
                "nom": pokemon.nom,
                "types": [pokemon.type_nom],
                "image": pokemon.image
            })
        else:
            next(p for p in pokemon_data if p['nom'] == pokemon.nom)['types'].append(pokemon.type_nom)

    return templates.TemplateResponse("view_db.html", {
        "request": request,
        "pokemon_data": pokemon_data
    })

JWT_SECRET_KEY = "your_secret_key"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 60 * 24 * 7

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

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
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/users/manage", status_code=status.HTTP_302_FOUND)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

from fastapi.responses import JSONResponse

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.post("/login")
async def login_for_access_token(response: Response, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)



