from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.auth import usuario_actual
from backend.db import get_conn

router = APIRouter(tags=["intereses"])


class InteresesIn(BaseModel):
    intereses: list[str] = Field(max_length=20)


def _estudiante(usuario):
    if usuario.get("rol") != "estudiante":
        raise HTTPException(status_code=403, detail="Acceso reservado a estudiantes")


@router.get("/intereses")
def leer_intereses(usuario=Depends(usuario_actual)):
    _estudiante(usuario)
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT area_interes FROM preferencias WHERE usuario_id=%s ORDER BY area_interes", (usuario["id"],))
        return {"intereses": [row[0] for row in cur.fetchall()]}


@router.put("/intereses")
def guardar_intereses(datos: InteresesIn, usuario=Depends(usuario_actual)):
    _estudiante(usuario)
    intereses = list(dict.fromkeys(i.strip().lower() for i in datos.intereses if i.strip()))
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("DELETE FROM preferencias WHERE usuario_id=%s", (usuario["id"],))
        if intereses:
            cur.executemany("INSERT INTO preferencias (usuario_id, area_interes) VALUES (%s,%s)",
                            [(usuario["id"], i) for i in intereses])
    return {"mensaje": "Intereses guardados", "intereses": intereses}
