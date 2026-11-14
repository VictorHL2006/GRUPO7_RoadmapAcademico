from fastapi import APIRouter, Depends, HTTPException
from pydantic import AliasChoices, BaseModel, EmailStr, Field
from psycopg2.errors import UniqueViolation

from backend.auth import clave_valida, crear_token, hash_clave, usuario_actual
from backend.db import get_conn

router = APIRouter(prefix="/auth", tags=["autenticación"])


class RegistroIn(BaseModel):
    codigo: str = Field(min_length=1, max_length=20)
    nombres: str = Field(min_length=1, max_length=100)
    correo: EmailStr
    clave: str = Field(min_length=8, max_length=128, validation_alias=AliasChoices("clave", "password"))


class LoginIn(BaseModel):
    correo: EmailStr
    clave: str = Field(min_length=1, max_length=128, validation_alias=AliasChoices("clave", "password"))


@router.post("/registro", status_code=201)
def registrar(datos: RegistroIn):
    try:
        with get_conn() as cn, cn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios (codigo, nombre, email, carrera, password_hash, rol) "
                "VALUES (%s, %s, %s, %s, %s, 'estudiante') RETURNING id",
                (datos.codigo.strip().upper(), datos.nombres.strip(), str(datos.correo).lower(),
                 "Por definir", hash_clave(datos.clave)),
            )
            usuario_id = cur.fetchone()[0]
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="El código o correo ya está registrado") from exc
    return {"mensaje": "Cuenta creada", "id": usuario_id}


@router.post("/login")
def login(datos: LoginIn):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT id, password_hash, rol, nombre FROM usuarios WHERE lower(email)=lower(%s)", (str(datos.correo),))
        usuario = cur.fetchone()
    if not usuario or not usuario[1] or not clave_valida(datos.clave, usuario[1]):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    return {"token": crear_token(usuario[0], usuario[2]), "rol": usuario[2], "nombre": usuario[3]}


@router.get("/yo")
def quien_soy(usuario=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT codigo, nombre, email, rol FROM usuarios WHERE id=%s", (usuario["id"],))
        fila = cur.fetchone()
    if not fila:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": usuario["id"], "codigo": fila[0], "nombres": fila[1],
            "correo": fila[2], "rol": fila[3]}
