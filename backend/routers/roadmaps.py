from fastapi import APIRouter, Depends, HTTPException, Response
from backend.auth import usuario_actual
from backend.db import get_conn

router = APIRouter()


@router.get("/roadmaps")
def listar_roadmaps(u=Depends(usuario_actual)):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("""SELECT id, codigo_verificacion, emitido_en, especialidad, creditos, hash_sha256
                       FROM roadmaps_emitidos WHERE usuario_id=%s
                       ORDER BY emitido_en DESC""", (u["id"],))
        return [{"id": i, "codigo": str(code), "codigo_verificacion": str(code),
                 "fecha": str(f)[:10], "especialidad": e, "creditos": c, "hash": h.strip()}
                for i, code, f, e, c, h in cur.fetchall()]


def _buscar_archivo(codigo: str, usuario: dict, campo: str):
    if campo not in {"archivo_pdf", "firma"}:
        raise ValueError("Campo no permitido")
    with get_conn() as cn, cn.cursor() as cur:
        if usuario.get("rol") == "tutor":
            cur.execute(
                f"SELECT {campo} FROM roadmaps_emitidos "
                "WHERE id::text=%s OR codigo_verificacion::text=%s",
                (codigo, codigo),
            )
        else:
            cur.execute(
                f"SELECT {campo} FROM roadmaps_emitidos WHERE usuario_id=%s "
                "AND (id::text=%s OR codigo_verificacion::text=%s)",
                (usuario["id"], codigo, codigo),
            )
        row = cur.fetchone()
    return row


@router.get("/roadmaps/{codigo}/pdf")
def descargar_pdf(codigo: str, u=Depends(usuario_actual)):
    row = _buscar_archivo(codigo, u, "archivo_pdf")
    if not row or row[0] is None:
        raise HTTPException(404, "Roadmap no encontrado")
    return Response(content=bytes(row[0]), media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="roadmap_{codigo}.pdf"'})


@router.get("/roadmaps/{codigo}/firma")
def descargar_firma(codigo: str, u=Depends(usuario_actual)):
    row = _buscar_archivo(codigo, u, "firma")
    if not row or row[0] is None:
        raise HTTPException(404, "Firma no encontrada")
    return Response(content=bytes(row[0]), media_type="application/octet-stream",
                    headers={"Content-Disposition": f'attachment; filename="roadmap_{codigo}.sig"'})
