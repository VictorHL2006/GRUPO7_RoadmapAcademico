"""Crea un usuario (por ejemplo un tutor) desde la terminal.

Uso:  python scripts/crear_usuario.py --codigo T001 --nombres "Tutor Prueba" \
          --correo tutor@ejemplo.com --rol tutor
La contraseña se pide por teclado (no queda en el historial de la terminal).
"""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend import config, servicios  # noqa: E402,F401

p = argparse.ArgumentParser()
p.add_argument("--codigo", required=True)
p.add_argument("--nombres", required=True)
p.add_argument("--correo", required=True)
p.add_argument("--rol", choices=["estudiante", "tutor"], default="estudiante")
a = p.parse_args()
clave = getpass.getpass("Contraseña (mínimo 8 caracteres): ")
if len(clave) < 8:
    sys.exit("La contraseña es muy corta.")
try:
    servicios.crear_usuario(a.codigo, a.nombres, a.correo, clave, a.rol)
except ValueError as e:
    sys.exit(str(e))
print(f"Usuario {a.codigo} creado con rol {a.rol}.")
