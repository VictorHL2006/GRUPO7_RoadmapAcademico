-- ROADMAP ACADÉMICO · esquema v2
-- ATENCIÓN: borra y recrea las tablas. Solo para desarrollo con datos ficticios.
DROP TABLE IF EXISTS roadmaps_emitidos, historial_academico, usuarios CASCADE;

CREATE TABLE usuarios (
    id                SERIAL PRIMARY KEY,
    codigo            VARCHAR(20)  UNIQUE NOT NULL,
    nombres           VARCHAR(100) NOT NULL,
    correo_hash       CHAR(64)     UNIQUE NOT NULL,   -- HMAC del correo: búsqueda y unicidad
    correo_cifrado    TEXT         NOT NULL,          -- AES-256-GCM
    password_hash     TEXT         NOT NULL,          -- scrypt
    rol               VARCHAR(12)  NOT NULL DEFAULT 'estudiante'
                      CHECK (rol IN ('estudiante', 'tutor')),
    intereses_cifrado TEXT,                           -- AES-256-GCM (lista en JSON)
    creado_en         TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE historial_academico (
    id           SERIAL PRIMARY KEY,
    usuario_id   INT         NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    codigo_curso VARCHAR(20) NOT NULL,
    nota_cifrada TEXT,                                -- AES-256-GCM
    aprobado     BOOLEAN     NOT NULL,
    periodo      VARCHAR(10),
    UNIQUE (usuario_id, codigo_curso)
);

CREATE TABLE roadmaps_emitidos (
    id                  SERIAL PRIMARY KEY,
    codigo_verificacion UUID        UNIQUE NOT NULL,  -- va dentro del QR
    usuario_id          INT         NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    especialidad        VARCHAR(100),
    pdf                 BYTEA       NOT NULL,
    hash_sha256         CHAR(64)    NOT NULL,
    firma               BYTEA       NOT NULL,         -- RSA-2048, PKCS#1 v1.5, SHA-256
    emitido_en          TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_historial_usuario ON historial_academico(usuario_id);
CREATE INDEX idx_roadmaps_usuario  ON roadmaps_emitidos(usuario_id);
