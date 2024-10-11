from fastapi import FastAPI, Depends, Request, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import PokemonType, Type, User
from fastapi.templating import Jinja2Templates
import matplotlib.pyplot as plt
from io import BytesIO

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get the database session
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
    type_distribution = db.query(Type.type_nom, func.count(PokemonType.numero).label('count'))\
        .join(Type, PokemonType.type_id == Type.type_id)\
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

@app.get("/pokemon/view_db", response_class=Response)
def view_db(db: Session = Depends(get_db), request: Request):
    # Query data from the database (just an example)
    pokemon_data = db.query(PokemonType).all()
    return templates.TemplateResponse("view_db.html", {"request": request, "pokemon_data": pokemon_data})
