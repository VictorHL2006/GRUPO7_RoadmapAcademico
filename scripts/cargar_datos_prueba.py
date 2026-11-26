"""Carga datos ficticios usando las variables DEMO_* del archivo .env."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv()

from backend.auth import hash_clave
from backend.db import get_conn


def main():
    estudiante_clave = os.getenv("DEMO_ESTUDIANTE_PASSWORD")
    tutor_clave = os.getenv("DEMO_TUTOR_PASSWORD")
    if not estudiante_clave or not tutor_clave:
        raise SystemExit("Configura DEMO_ESTUDIANTE_PASSWORD y DEMO_TUTOR_PASSWORD en .env")
    with get_conn() as cn, cn.cursor() as cur:
        for codigo, nombre, correo, clave, rol in (
            ("E901", "Ana Prueba Lopez", "ana@ejemplo.com", estudiante_clave, "estudiante"),
            ("T901", "Tutor Prueba", "tutor@ejemplo.com", tutor_clave, "tutor"),
        ):
            cur.execute(
                "INSERT INTO usuarios (codigo,nombre,email,carrera,password_hash,rol) "
                "VALUES (%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (codigo) DO UPDATE SET nombre=EXCLUDED.nombre, "
                "email=EXCLUDED.email, password_hash=EXCLUDED.password_hash, rol=EXCLUDED.rol",
                (codigo, nombre, correo, "Ingeniería de Sistemas", hash_clave(clave), rol),
            )
        cur.execute("SELECT id FROM usuarios WHERE codigo='E901'")
        usuario_id = cur.fetchone()[0]
        cur.execute("DELETE FROM preferencias WHERE usuario_id=%s", (usuario_id,))
        cur.executemany(
            "INSERT INTO preferencias (usuario_id,area_interes) VALUES (%s,%s)",
            [(usuario_id, "redes"), (usuario_id, "seguridad")],
        )
        cur.execute("DELETE FROM historial_academico WHERE usuario_id=%s", (usuario_id,))
        cur.executemany(
            "INSERT INTO historial_academico (usuario_id,curso,nota,periodo) VALUES (%s,%s,%s,%s)",
            [(usuario_id, "MAT101", 15, "2025-I"), (usuario_id, "PRG101", 16, "2025-I")],
        )
    print("Datos ficticios cargados: E901 y T901. Las claves provienen de .env.")


if __name__ == "__main__":
    main()
