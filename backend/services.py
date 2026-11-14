"""Servicios compartidos para generar, emitir y verificar roadmaps."""

import os
from pathlib import Path
from uuid import uuid4

from backend.db import get_conn
from backend.pdf.firma import firmar_pdf
from backend.pdf.generador import generar_pdf
from backend.recomendacion.motor import cargar_json, generar_recomendacion


RAIZ = Path(__file__).resolve().parents[1]


def recomendar_para_usuario(usuario_id: int, max_creditos: int = 22) -> dict | None:
    """Calcula una recomendación con el historial e intereses persistidos."""
    malla_path = Path(os.getenv("MALLA_PATH", str(RAIZ / "data" / "malla.json")))
    if not malla_path.is_file():
        raise FileNotFoundError("No se encontró data/malla.json")

    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("SELECT codigo, nombre FROM usuarios WHERE id=%s", (usuario_id,))
        estudiante = cur.fetchone()
        if not estudiante:
            return None
        cur.execute(
            "SELECT curso FROM historial_academico WHERE usuario_id=%s AND nota >= 12",
            (usuario_id,),
        )
        aprobados = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT area_interes FROM preferencias WHERE usuario_id=%s", (usuario_id,))
        intereses = [row[0] for row in cur.fetchall()]

    return generar_recomendacion(
        cargar_json(malla_path),
        {"codigo": estudiante[0], "nombre": estudiante[1],
         "aprobados": aprobados, "intereses": intereses},
        max_creditos,
    )


def emitir_para_usuario(usuario_id: int, max_creditos: int = 22) -> dict | None:
    """Crea el PDF, su firma desacoplada y un código público de verificación."""
    rec = recomendar_para_usuario(usuario_id, max_creditos)
    if rec is None:
        return None

    codigo = str(uuid4())
    api_base = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
    pdf = generar_pdf(rec, f"{api_base}/v/{codigo}")
    hash_hex, firma = firmar_pdf(pdf)
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute(
            """INSERT INTO roadmaps_emitidos
               (usuario_id, codigo_verificacion, hash_sha256, firma, archivo_pdf,
                especialidad, creditos)
               VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (usuario_id, codigo, hash_hex, firma, pdf, rec["especialidad"], rec["creditos"]),
        )
        roadmap_id = cur.fetchone()[0]

    return {
        "id": roadmap_id,
        "codigo": codigo,
        "codigo_verificacion": codigo,
        "especialidad": rec["especialidad"],
        "puntajes": rec["puntajes"],
        "cursos": rec["cursos"],
        "creditos": rec["creditos"],
        "hash": hash_hex,
    }
