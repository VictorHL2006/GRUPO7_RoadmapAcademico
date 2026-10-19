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
        return [{"id": i, "fecha": str(f)[:10], "especialidad": e, "creditos": c, "hash": h.strip()}
                for i, f, e, c, h in cur.fetchall()]


@router.get("/roadmaps/{roadmap_id}/pdf")
def descargar_pdf(roadmap_id: int, u=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT archivo_pdf FROM roadmaps_emitidos WHERE id=%s AND usuario_id=%s",
                    (roadmap_id, u["id"]))
        row = cur.fetchone()
    if not row or row[0] is None:
        raise HTTPException(404, "Roadmap no encontrado")
    return Response(content=bytes(row[0]), media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="roadmap_{roadmap_id}.pdf"'})


@router.get("/roadmaps/{roadmap_id}/firma")
def descargar_firma(roadmap_id: int, u=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT firma FROM roadmaps_emitidos WHERE id=%s AND usuario_id=%s",
                    (roadmap_id, u["id"]))
        row = cur.fetchone()
    if not row or row[0] is None:
        raise HTTPException(404, "Firma no encontrada")
    return Response(content=bytes(row[0]), media_type="application/octet-stream",
                    headers={"Content-Disposition": f'attachment; filename="roadmap_{roadmap_id}.sig"'})
