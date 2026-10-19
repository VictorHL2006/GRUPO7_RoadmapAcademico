import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import usuario_actual
from backend.db import get_conn
from backend.pdf.firma import firmar_pdf
from backend.pdf.generador import generar_pdf
from backend.recomendacion.motor import cargar_json, generar_recomendacion

router = APIRouter(tags=["roadmap"])
RAIZ = Path(__file__).resolve().parents[2]
MALLA_PATH = Path(os.getenv("MALLA_PATH", str(RAIZ / "data" / "malla.json")))


@router.post("/roadmap/generar")
def generar(max_creditos: int = Query(default=22, ge=1, le=40), usuario=Depends(usuario_actual)):
    if usuario.get("rol") != "estudiante":
        raise HTTPException(status_code=403, detail="Solo un estudiante puede generar un roadmap")
    if not MALLA_PATH.exists():
        raise HTTPException(status_code=500, detail="No se encontró data/malla.json")
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT codigo, nombre FROM usuarios WHERE id=%s", (usuario["id"],))
        estudiante = cur.fetchone()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        cur.execute("SELECT curso FROM historial_academico WHERE usuario_id=%s AND nota >= 12", (usuario["id"],))
        aprobados = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT area_interes FROM preferencias WHERE usuario_id=%s", (usuario["id"],))
        intereses = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT nextval(pg_get_serial_sequence('roadmaps_emitidos','id'))")
        roadmap_id = cur.fetchone()[0]
        rec = generar_recomendacion(cargar_json(MALLA_PATH),
                                    {"codigo": estudiante[0], "nombre": estudiante[1],
                                     "aprobados": aprobados, "intereses": intereses}, max_creditos)
        rec["estudiante"] = estudiante[0]
        verify_base = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
        pdf = generar_pdf(rec, f"{verify_base}/verificar.html?id={roadmap_id}")
        hash_hex, firma = firmar_pdf(pdf)
        cur.execute("""INSERT INTO roadmaps_emitidos
                       (id, usuario_id, hash_sha256, firma, archivo_pdf, especialidad, creditos)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (roadmap_id, usuario["id"], hash_hex, firma, pdf, rec["especialidad"], rec["creditos"]))
    return {"id": roadmap_id, "especialidad": rec["especialidad"], "puntajes": rec["puntajes"],
            "cursos": rec["cursos"], "creditos": rec["creditos"], "hash": hash_hex}
