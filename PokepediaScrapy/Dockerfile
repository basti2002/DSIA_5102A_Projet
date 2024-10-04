FROM python:3.10

# Définit le dossier de travail
WORKDIR /app

# Copie le requirements.txt 
COPY ./PokepediaScrapy/requirements.txt /app/

RUN pip install -r /app/requirements.txt

# Copier le projet Scrapy 
COPY ./PokepediaScrapy /app/PokepediaScrapy
COPY ./scrapy.cfg /app/


# Définit le dossier de travail
WORKDIR /app/PokepediaScrapy

# On run le Scrapy et l'insertion des données 
CMD scrapy crawl pokemon && scrapy crawl pokemon_detail && python insert.py
