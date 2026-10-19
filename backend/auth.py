import os
import time
import hashlib
import hmac
import secrets

import jwt
from fastapi import Header, HTTPException
from jwt import PyJWTError

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 3600


def _secret():
    secret = os.getenv("JWT_SECRET", JWT_SECRET)
    if not secret or len(secret) < 32:
        raise RuntimeError("JWT_SECRET debe configurarse con al menos 32 caracteres.")
    return secret


def hash_clave(clave: str, sal: bytes | None = None) -> str:
    if not clave:
        raise ValueError("La contraseña no puede estar vacía.")
    sal = sal or secrets.token_bytes(16)
    derivada = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, 200_000)
    return f"{sal.hex()}:{derivada.hex()}"


def clave_valida(clave: str, guardado: str) -> bool:
    try:
        sal_hex, hash_hex = guardado.split(":", 1)
        derivada = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), bytes.fromhex(sal_hex), 200_000)
        return hmac.compare_digest(derivada.hex(), hash_hex)
    except (ValueError, TypeError):
        return False


def crear_token(usuario_id: int, rol: str) -> str:
    ahora = int(time.time())
    claims = {"sub": str(usuario_id), "rol": rol, "iat": ahora, "exp": ahora + TOKEN_TTL_SECONDS}
    return jwt.encode(claims, _secret(), algorithm=JWT_ALGORITHM)


def usuario_actual(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="No autenticado", headers={"WWW-Authenticate": "Bearer"})
    token = authorization.split(None, 1)[1]
    try:
        claims = jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])
        return {"id": int(claims["sub"]), "rol": claims["rol"]}
    except (PyJWTError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada", headers={"WWW-Authenticate": "Bearer"}) from exc


def exigir_tutor(usuario: dict) -> dict:
    if usuario.get("rol") != "tutor":
        raise HTTPException(status_code=403, detail="Acceso reservado al rol tutor")
    return usuario
