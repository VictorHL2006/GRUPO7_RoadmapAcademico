CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    carrera VARCHAR(100) NOT NULL
);

CREATE TABLE preferencias (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    area_interes VARCHAR(100) NOT NULL
);

CREATE TABLE historial_academico (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    curso VARCHAR(100) NOT NULL,
    nota DECIMAL(4,2) NOT NULL
);