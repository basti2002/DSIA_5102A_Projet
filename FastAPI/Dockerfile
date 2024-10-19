FROM python:3.10

# Définit le dossier de travail
WORKDIR /app

# Copie le fichier requirements.txt spécifique à FastAPI
COPY ./FastAPI/requirements.txt /app/

# Installe les dépendances
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copie le reste de l'application FastAPI dans le conteneur
COPY ./FastAPI/app /app

COPY ./FastAPI/static /static
# Commande pour lancer l'application FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
