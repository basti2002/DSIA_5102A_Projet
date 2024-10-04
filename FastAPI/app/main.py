from fastapi import FastAPI, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import PokemonType, Type
import matplotlib.pyplot as plt
from io import BytesIO

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/pokemon/type_count", response_class=Response)
def read_type_distribution(db: Session = Depends(get_db)):
    type_distribution = db.query(Type.type_nom, func.count(PokemonType.numero).label('count')).\
        join(Type, PokemonType.type_id == Type.type_id).\
        group_by(Type.type_nom).all()

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