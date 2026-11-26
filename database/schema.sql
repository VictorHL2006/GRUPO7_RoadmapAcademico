-- Esquema de la versión actual de la API. Idempotente y no destructivo.
-- Para instalaciones nuevas o actualización desde el esquema legado.

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    carrera VARCHAR(100) NOT NULL DEFAULT 'Por definir',
    password_hash TEXT NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'estudiante'
        CHECK (rol IN ('estudiante', 'tutor'))
);

ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS codigo VARCHAR(20);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email VARCHAR(254);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS carrera VARCHAR(100) NOT NULL DEFAULT 'Por definir';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol VARCHAR(20) NOT NULL DEFAULT 'estudiante';
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='nombres') THEN
        UPDATE usuarios SET nombre = nombres WHERE nombre IS NULL;
        ALTER TABLE usuarios ALTER COLUMN nombres DROP NOT NULL;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='correo_hash') THEN
        ALTER TABLE usuarios ALTER COLUMN correo_hash DROP NOT NULL;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='correo_cifrado') THEN
        ALTER TABLE usuarios ALTER COLUMN correo_cifrado DROP NOT NULL;
    END IF;
END $$;
CREATE UNIQUE INDEX IF NOT EXISTS usuarios_codigo_uq ON usuarios (codigo);
CREATE UNIQUE INDEX IF NOT EXISTS usuarios_email_uq ON usuarios (email);

CREATE TABLE IF NOT EXISTS preferencias (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    area_interes VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS historial_academico (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    curso VARCHAR(100) NOT NULL,
    nota NUMERIC(4,2) NOT NULL CHECK (nota >= 0 AND nota <= 20),
    periodo VARCHAR(10)
);
ALTER TABLE historial_academico ADD COLUMN IF NOT EXISTS periodo VARCHAR(10);
ALTER TABLE historial_academico ADD COLUMN IF NOT EXISTS curso VARCHAR(100);
ALTER TABLE historial_academico ADD COLUMN IF NOT EXISTS nota NUMERIC(4,2);
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='historial_academico' AND column_name='codigo_curso') THEN
        UPDATE historial_academico SET curso = codigo_curso WHERE curso IS NULL;
        ALTER TABLE historial_academico ALTER COLUMN codigo_curso DROP NOT NULL;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='historial_academico' AND column_name='aprobado') THEN
        ALTER TABLE historial_academico ALTER COLUMN aprobado DROP NOT NULL;
    END IF;
END $$;
UPDATE historial_academico SET curso = 'LEGACY-' || id::text WHERE curso IS NULL;
UPDATE historial_academico SET nota = 0 WHERE nota IS NULL;
ALTER TABLE historial_academico ALTER COLUMN curso SET NOT NULL;
ALTER TABLE historial_academico ALTER COLUMN nota SET NOT NULL;
CREATE INDEX IF NOT EXISTS idx_historial_usuario ON historial_academico (usuario_id);

CREATE TABLE IF NOT EXISTS roadmaps_emitidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    hash_sha256 CHAR(64) NOT NULL,
    firma BYTEA NOT NULL,
    archivo_pdf BYTEA NOT NULL,
    codigo_verificacion UUID NOT NULL DEFAULT gen_random_uuid(),
    especialidad VARCHAR(100),
    creditos INTEGER,
    emitido_en TIMESTAMP NOT NULL DEFAULT NOW()
);
ALTER TABLE roadmaps_emitidos ADD COLUMN IF NOT EXISTS archivo_pdf BYTEA;
ALTER TABLE roadmaps_emitidos ADD COLUMN IF NOT EXISTS codigo_verificacion UUID;
ALTER TABLE roadmaps_emitidos ADD COLUMN IF NOT EXISTS especialidad VARCHAR(100);
ALTER TABLE roadmaps_emitidos ADD COLUMN IF NOT EXISTS creditos INTEGER;
ALTER TABLE roadmaps_emitidos ADD COLUMN IF NOT EXISTS emitido_en TIMESTAMP NOT NULL DEFAULT NOW();
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='roadmaps_emitidos' AND column_name='pdf') THEN
        UPDATE roadmaps_emitidos SET archivo_pdf = pdf WHERE archivo_pdf IS NULL;
        ALTER TABLE roadmaps_emitidos ALTER COLUMN pdf DROP NOT NULL;
    END IF;
END $$;
UPDATE roadmaps_emitidos SET codigo_verificacion = gen_random_uuid()
WHERE codigo_verificacion IS NULL;
UPDATE roadmaps_emitidos SET archivo_pdf = '\x'::bytea WHERE archivo_pdf IS NULL;
ALTER TABLE roadmaps_emitidos ALTER COLUMN archivo_pdf SET NOT NULL;
ALTER TABLE roadmaps_emitidos ALTER COLUMN codigo_verificacion SET DEFAULT gen_random_uuid();
ALTER TABLE roadmaps_emitidos ALTER COLUMN codigo_verificacion SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS roadmaps_emitidos_codigo_verificacion_uq
    ON roadmaps_emitidos (codigo_verificacion);
CREATE INDEX IF NOT EXISTS idx_roadmaps_usuario ON roadmaps_emitidos (usuario_id);
