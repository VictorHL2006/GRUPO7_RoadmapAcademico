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
CREATE TABLE IF NOT EXISTS roadmaps_emitidos (
    id           SERIAL PRIMARY KEY,
    usuario_id   INT NOT NULL REFERENCES usuarios(id),
    hash_sha256  CHAR(64) NOT NULL,
    firma        BYTEA NOT NULL,
    archivo_pdf  BYTEA,
    especialidad VARCHAR(100),
    creditos     INT,
    emitido_en   TIMESTAMP DEFAULT NOW()
);

ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS codigo VARCHAR(20) UNIQUE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_hash VARCHAR(200);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol VARCHAR(20) DEFAULT 'estudiante';

ALTER TABLE historial_academico ADD COLUMN IF NOT EXISTS periodo VARCHAR(10);