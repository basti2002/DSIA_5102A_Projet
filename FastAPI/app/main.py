from fastapi import FastAPI, Depends, Request, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import Pokemon, PokemonType, Type
from fastapi.templating import Jinja2Templates
import matplotlib.pyplot as plt
from io import BytesIO
from sqlalchemy.orm import joinedload

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




