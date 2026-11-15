"""Hash SHA-256 y firma digital RSA (PKCS#1 v1.5).

Es compatible con los scripts de OpenSSL del proyecto:
    openssl dgst -sha256 -sign keys/private_key.pem -out doc.sig doc
    openssl dgst -sha256 -verify keys/public_key.pem -signature doc.sig doc
"""
import hashlib
import os
from functools import lru_cache

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def sha256_hex(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


@lru_cache(maxsize=4)
def _cargar_privada(ruta: str):
    with open(ruta, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


@lru_cache(maxsize=4)
def _cargar_publica(ruta: str):
    with open(ruta, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def firmar(datos: bytes, ruta_privada: str | None = None) -> bytes:
    ruta = ruta_privada or os.getenv("PRIVATE_KEY_PATH", "keys/private_key.pem")
    return _cargar_privada(ruta).sign(datos, padding.PKCS1v15(), hashes.SHA256())


def verificar(datos: bytes, firma: bytes, ruta_publica: str | None = None) -> bool:
    ruta = ruta_publica or os.getenv("PUBLIC_KEY_PATH", "keys/public_key.pem")
    try:
        _cargar_publica(ruta).verify(firma, datos, padding.PKCS1v15(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False
