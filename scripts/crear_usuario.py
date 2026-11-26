"""Crea una cuenta de estudiante o tutor solicitando la contraseña en consola."""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv()

from backend.auth import hash_clave
from backend.db import get_conn


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codigo", required=True)
    parser.add_argument("--nombres", required=True)
    parser.add_argument("--correo", required=True)
    parser.add_argument("--rol", choices=("estudiante", "tutor"), default="estudiante")
    args = parser.parse_args()
    clave = getpass.getpass("Contraseña (mínimo 8 caracteres): ")
    if len(clave) < 8:
        parser.error("la contraseña debe tener al menos 8 caracteres")
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute(
            "INSERT INTO usuarios (codigo,nombre,email,carrera,password_hash,rol) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (args.codigo.strip().upper(), args.nombres.strip(), args.correo.strip().lower(),
             "Por definir", hash_clave(clave), args.rol),
        )
    print(f"Usuario {args.codigo.strip().upper()} creado con rol {args.rol}.")


if __name__ == "__main__":
    main()
