CREATE TABLE pokemon (
    numero INT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    image_mini VARCHAR(255),
    lien VARCHAR(255),
    image VARCHAR(255)
);

CREATE TABLE type (
    type_id SERIAL PRIMARY KEY,
    type_nom VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE pokemon_type (
    numero INT,
    type_id INT,
    FOREIGN KEY (numero) REFERENCES pokemon(numero),
    FOREIGN KEY (type_id) REFERENCES type(type_id),
    PRIMARY KEY (numero, type_id)
);

CREATE TABLE statistiques (
    numero INT,
    pv INT,
    attaque INT,
    defense INT,
    attaque_speciale INT,
    defense_speciale INT,
    vitesse INT,
    special INT,
    FOREIGN KEY (numero) REFERENCES pokemon(numero),
    PRIMARY KEY (numero)
);

CREATE TABLE evolution (
    numero INT,
    evolution VARCHAR(255),
    FOREIGN KEY (numero) REFERENCES pokemon(numero),
    PRIMARY KEY (numero, evolution)
);

CREATE TABLE sensibilite (
    sensibilite_id SERIAL PRIMARY KEY,
    valeur FLOAT NOT NULL UNIQUE
);

CREATE TABLE pokemon_sensibilite (
    numero INT,
    type_id INT,
    sensibilite_id INT,
    FOREIGN KEY (numero) REFERENCES pokemon(numero),
    FOREIGN KEY (type_id) REFERENCES type(type_id),
    FOREIGN KEY (sensibilite_id) REFERENCES sensibilite(sensibilite_id),
    PRIMARY KEY (numero, type_id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
);

CREATE TABLE user_pokemon_team (
    user_id INT,
    pokemon_id INT,
    slot INT CHECK (slot BETWEEN 0 AND 6),
    PRIMARY KEY (user_id, slot),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(numero)
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);





