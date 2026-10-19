import os

from dotenv import load_dotenv

from backend.auth import hash_clave
from backend.db import get_conn

load_dotenv()


def upsert_demo(cur, codigo, nombre, correo, clave, rol):
    cur.execute("SELECT id FROM usuarios WHERE codigo=%s OR lower(email)=lower(%s)", (codigo, correo))
    encontrado = cur.fetchone()
    if encontrado:
        cur.execute("""UPDATE usuarios SET codigo=%s, nombre=%s, email=%s, carrera=%s,
                       password_hash=%s, rol=%s WHERE id=%s""",
                    (codigo, nombre, correo, "Ingeniería de Sistemas", hash_clave(clave), rol, encontrado[0]))
    else:
        cur.execute("""INSERT INTO usuarios (codigo,nombre,email,carrera,password_hash,rol)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (codigo, nombre, correo, "Ingeniería de Sistemas", hash_clave(clave), rol))


def main():
    with get_conn() as cn, cn.cursor() as cur:
        upsert_demo(cur, "E001", "Estudiante Demo", "e001@demo.local",
                    os.getenv("DEMO_ESTUDIANTE_PASSWORD", "Demo-E001-2026"), "estudiante")
        upsert_demo(cur, "T001", "Tutor Demo", "t001@demo.local",
                    os.getenv("DEMO_TUTOR_PASSWORD", "Demo-T001-2026"), "tutor")
    print("Usuarios demo listos: E001 y T001.")
    print("Credenciales de demostración únicamente; cambia DEMO_*_PASSWORD antes de exponer el entorno.")


if __name__ == "__main__":
    main()
