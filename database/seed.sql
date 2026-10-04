INSERT INTO usuarios (nombre, email, carrera) VALUES
('Hugo Quiroz', 'hugo.quiroz@ucsm.edu.pe', 'Ingeniería de Sistemas'),
('Victor Humpiri', 'victor.humpiri@ucsm.edu.pe', 'Ingeniería de Sistemas'),
('Leroy Román', 'leroy.roman@ucsm.edu.pe', 'Ingeniería de Sistemas'),
('Patrick Minaya', 'patrick.minaya@ucsm.edu.pe', 'Ingeniería de Sistemas');

INSERT INTO preferencias (usuario_id, area_interes) VALUES
(1, 'Redes y Ciberseguridad'),
(2, 'Desarrollo Backend'),
(3, 'Bases de Datos'),
(4, 'Arquitectura de Software');

INSERT INTO historial_academico (usuario_id, curso, nota) VALUES
(1, 'Fundamentos de Conmutación y Enrutamiento', 18.5),
(2, 'Programación Orientada a Objetos', 17.0),
(3, 'Diseño de Base de Datos', 19.0),
(4, 'Sistemas Operativos', 16.5);