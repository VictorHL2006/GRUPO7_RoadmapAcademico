-- Datos ficticios para pruebas internas. Las cuentas usan un hash bloqueado y
-- no pueden iniciar sesión; para cuentas funcionales usa scripts/cargar_demo.py.
INSERT INTO usuarios (codigo, nombre, email, carrera, password_hash, rol) VALUES
('E901', 'Ana Prueba Lopez', 'ana.seed@example.com', 'Ingeniería de Sistemas', 'SEED_LOGIN_DISABLED', 'estudiante'),
('E902', 'Bruno Prueba', 'bruno.seed@example.com', 'Ingeniería de Sistemas', 'SEED_LOGIN_DISABLED', 'estudiante')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO preferencias (usuario_id, area_interes)
SELECT u.id, v.area
FROM usuarios u
JOIN (VALUES ('E901', 'redes'), ('E901', 'seguridad'), ('E902', 'datos')) AS v(codigo, area)
  ON u.codigo = v.codigo
WHERE NOT EXISTS (
    SELECT 1 FROM preferencias p WHERE p.usuario_id = u.id AND p.area_interes = v.area
);

INSERT INTO historial_academico (usuario_id, curso, nota, periodo)
SELECT u.id, v.curso, v.nota, '2025-I'
FROM usuarios u
JOIN (VALUES ('E901', 'MAT101', 15.0), ('E901', 'PRG101', 16.0), ('E902', 'MAT101', 14.0))
    AS v(codigo, curso, nota) ON u.codigo = v.codigo
WHERE NOT EXISTS (
    SELECT 1 FROM historial_academico h WHERE h.usuario_id = u.id AND h.curso = v.curso
);
