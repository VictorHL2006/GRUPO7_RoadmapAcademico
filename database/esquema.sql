CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    carrera VARCHAR(100) NOT NULL DEFAULT 'Por definir',
    password_hash VARCHAR(200),
    rol VARCHAR(20) NOT NULL DEFAULT 'estudiante' CHECK (rol IN ('estudiante', 'tutor'))
);

ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS codigo VARCHAR(20) UNIQUE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_hash VARCHAR(200);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol VARCHAR(20) NOT NULL DEFAULT 'estudiante';

CREATE TABLE IF NOT EXISTS preferencias (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    area_interes VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS historial_academico (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    curso VARCHAR(100) NOT NULL,
    nota DECIMAL(4,2) NOT NULL CHECK (nota >= 0 AND nota <= 20),
    periodo VARCHAR(10)
);
ALTER TABLE historial_academico ADD COLUMN IF NOT EXISTS periodo VARCHAR(10);

CREATE TABLE IF NOT EXISTS roadmaps_emitidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    hash_sha256 CHAR(64) NOT NULL,
    firma BYTEA NOT NULL,
    archivo_pdf BYTEA,
    especialidad VARCHAR(100),
    creditos INTEGER,
    emitido_en TIMESTAMP NOT NULL DEFAULT NOW()
);
ALTER TABLE roadmaps_emitidos ADD COLUMN IF NOT EXISTS archivo_pdf BYTEA;
