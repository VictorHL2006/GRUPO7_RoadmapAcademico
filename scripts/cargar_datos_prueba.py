"""Crea usuarios FICTICIOS para probar y hacer capturas (solo desarrollo).

Crea: estudiante E901 (ana@ejemplo.com) con historial e intereses, y tutor T001
(tutor@ejemplo.com). Contraseña de ambos: Prueba123!   -> NO usar en producción.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend import config, db, servicios  # noqa: E402,F401
from crypto import cifrado  # noqa: E402

CLAVE = "Prueba123!"
for datos in (("E901", "Ana Prueba Lopez", "ana@ejemplo.com", "estudiante"),
              ("T001", "Tutor Prueba", "tutor@ejemplo.com", "tutor")):
    try:
        servicios.crear_usuario(datos[0], datos[1], datos[2], CLAVE, datos[3])
        print("Creado:", datos[0])
    except ValueError:
        print("Ya existía:", datos[0])

with db.cursor() as cur:
    cur.execute("SELECT id FROM usuarios WHERE codigo = 'E901'")
    uid = cur.fetchone()["id"]
    cur.execute("UPDATE usuarios SET intereses_cifrado = %s WHERE id = %s",
                (cifrado.cifrar(json.dumps(["redes", "seguridad"]), "usuarios.intereses"), uid))
    for curso, nota in (("MAT101", 15.0), ("PRG101", 16.0)):
        cur.execute("""INSERT INTO historial_academico
                       (usuario_id, codigo_curso, nota_cifrada, aprobado, periodo)
                       VALUES (%s, %s, %s, TRUE, '2025-I') ON CONFLICT DO NOTHING""",
                    (uid, curso, cifrado.cifrar(str(nota), "historial.nota")))
print("Listo. Entrar con ana@ejemplo.com o tutor@ejemplo.com  (clave: Prueba123!)")
