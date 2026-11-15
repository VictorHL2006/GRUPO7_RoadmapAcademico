"""Hash de contraseñas con scrypt (biblioteca estándar, sin dependencias extra).

Las contraseñas NO se cifran: se les aplica un hash lento con sal, que no se revierte.
Formato guardado:  scrypt$N$r$p$sal_b64$hash_b64
"""
import base64
import hashlib
import hmac
import os

_N, _R, _P, _LEN = 2 ** 14, 8, 1, 32


def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def hashear(password: str) -> str:
    sal = os.urandom(16)
    h = hashlib.scrypt(password.encode("utf-8"), salt=sal, n=_N, r=_R, p=_P, dklen=_LEN)
    return f"scrypt${_N}${_R}${_P}${_b64(sal)}${_b64(h)}"


def verificar(password: str, almacenado: str) -> bool:
    try:
        _, n, r, p, sal, esperado = almacenado.split("$")
        h = hashlib.scrypt(password.encode("utf-8"), salt=base64.b64decode(sal),
                           n=int(n), r=int(r), p=int(p), dklen=_LEN)
        return hmac.compare_digest(h, base64.b64decode(esperado))
    except (ValueError, TypeError):
        return False


# Se usa cuando el usuario no existe, para que login tarde igual y no revele qué correos hay.
HASH_FALSO = hashear("contraseña-falsa-para-igualar-tiempos")
