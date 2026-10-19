from fastapi import APIRouter, Depends, HTTPException, Response
from backend.auth import usuario_actual
from backend.db import get_conn

router = APIRouter()


@router.get("/roadmaps")
def listar_roadmaps(u=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("""SELECT id, emitido_en, especialidad, creditos, hash_sha256
                       FROM roadmaps_emitidos WHERE usuario_id=%s
                       ORDER BY emitido_en DESC""", (u["id"],))
        return [{"id": i, "fecha": str(f)[:10], "especialidad": e, "creditos": c, "hash": h}
                for i, f, e, c, h in cur.fetchall()]


@router.get("/roadmaps/{id}/pdf")
def descargar(id: int, u=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT archivo_pdf FROM roadmaps_emitidos WHERE id=%s AND usuario_id=%s",
                    (id, u["id"]))
        f = cur.fetchone()
    if not f or f[0] is None:
        raise HTTPException(404, "Roadmap no encontrado")
    return Response(content=bytes(f[0]), media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="roadmap_{id}.pdf"'})