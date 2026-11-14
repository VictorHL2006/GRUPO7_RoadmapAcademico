from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from psycopg2.errors import UniqueViolation
from backend.auth import usuario_actual
from backend.db import get_conn

router = APIRouter()

NOTA_MINIMA = 12  # criterio de aprobado, configurable


class PerfilIn(BaseModel):
    nombres: str = Field(min_length=1, max_length=100)
    correo: EmailStr


class CursoIn(BaseModel):
    codigo_curso: str = Field(min_length=1, max_length=100)
    nota: float = Field(ge=0, le=20)
    periodo: str = Field(default="-", max_length=10)


class HistorialIn(BaseModel):
    cursos: list[CursoIn]


@router.get("/perfil")
def leer_perfil(u=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT codigo, nombre, email FROM usuarios WHERE id=%s", (u["id"],))
        f = cur.fetchone()
        if not f:
            raise HTTPException(404, "Usuario no encontrado")
        cur.execute("SELECT area_interes FROM preferencias WHERE usuario_id=%s", (u["id"],))
        intereses = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) FROM historial_academico WHERE usuario_id=%s AND nota>=%s",
                    (u["id"], NOTA_MINIMA))
        aprobados = cur.fetchone()[0]
    # creditos: se calcula con data/malla.json (pendiente de conectar)
    return {"codigo": f[0], "nombres": f[1], "correo": f[2],
            "intereses": intereses, "cursos_aprobados": aprobados, "creditos": None}


@router.put("/perfil")
def actualizar_perfil(d: PerfilIn, u=Depends(usuario_actual)):
    try:
        with get_conn() as cn, cn.cursor() as cur:
            cur.execute("UPDATE usuarios SET nombre=%s, email=%s WHERE id=%s",
                        (d.nombres.strip(), str(d.correo).lower(), u["id"]))
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="El correo ya está registrado") from exc
    return {"mensaje": "Perfil actualizado"}


@router.get("/historial")
def listar_historial(u=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("""SELECT curso, nota, COALESCE(periodo, '-')
                       FROM historial_academico WHERE usuario_id=%s
                       ORDER BY periodo DESC NULLS LAST, curso""", (u["id"],))
        return [{"codigo_curso": c, "nota": float(n), "aprobado": float(n) >= NOTA_MINIMA, "periodo": p}
                for c, n, p in cur.fetchall()]


@router.post("/historial")
def agregar_curso(d: CursoIn, u=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("""INSERT INTO historial_academico (usuario_id, curso, nota, periodo)
                       VALUES (%s,%s,%s,%s)""",
                    (u["id"], d.codigo_curso.upper(), d.nota, d.periodo))
    return {"mensaje": "Curso agregado"}


@router.put("/historial")
def reemplazar_historial(
    datos: list[CursoIn] | HistorialIn = Body(...), u=Depends(usuario_actual)
):
    cursos = datos.cursos if isinstance(datos, HistorialIn) else datos
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("DELETE FROM historial_academico WHERE usuario_id=%s", (u["id"],))
        if cursos:
            cur.executemany(
                """INSERT INTO historial_academico (usuario_id, curso, nota, periodo)
                   VALUES (%s,%s,%s,%s)""",
                [(u["id"], curso.codigo_curso.strip().upper(), curso.nota, curso.periodo)
                 for curso in cursos],
            )
    return {"mensaje": "Historial actualizado", "cursos": len(cursos)}
