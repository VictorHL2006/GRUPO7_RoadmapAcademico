"""Cifrado AES-256-GCM de columnas sensibles e índice ciego para búsquedas.

- La clave maestra (32 bytes en base64) viene de la variable ENCRYPTION_KEY.
- Cada valor usa un nonce aleatorio de 12 bytes, guardado junto al texto cifrado.
- El "contexto" (por ejemplo "usuarios.correo") se autentica como dato asociado:
  un valor copiado a otra columna ya no se puede descifrar.
- indice_ciego() da un HMAC estable para buscar o exigir unicidad sin guardar el
  dato en claro (el correo cifrado, por sí solo, no se puede buscar).
"""
import base64
import os

from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def _clave_maestra() -> bytes:
    b64 = os.getenv("ENCRYPTION_KEY")
    if not b64:
        raise RuntimeError("Falta ENCRYPTION_KEY en el entorno (.env). "
                           "Generarla con: python scripts/generar_secretos.py")
    clave = base64.b64decode(b64)
    if len(clave) != 32:
        raise RuntimeError("ENCRYPTION_KEY debe contener exactamente 32 bytes en base64.")
    return clave


def _clave_indice() -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"roadmap-indice-ciego").derive(_clave_maestra())


def cifrar(texto: str, contexto: str = "") -> str:
    nonce = os.urandom(12)
    datos = AESGCM(_clave_maestra()).encrypt(
        nonce, texto.encode("utf-8"), contexto.encode("utf-8") or None)
    return base64.b64encode(nonce + datos).decode("ascii")


def descifrar(token: str, contexto: str = "") -> str:
    crudo = base64.b64decode(token)
    nonce, datos = crudo[:12], crudo[12:]
    return AESGCM(_clave_maestra()).decrypt(
        nonce, datos, contexto.encode("utf-8") or None).decode("utf-8")


def indice_ciego(texto: str) -> str:
    h = hmac.HMAC(_clave_indice(), hashes.SHA256())
    h.update(texto.strip().lower().encode("utf-8"))
    return h.finalize().hex()
