import hashlib
import os
from pathlib import Path

from cryptography.exceptions import InvalidKey, InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.db import get_conn

router = APIRouter(tags=["verificación"])


def _verificar(pdf: bytes, firma: bytes) -> bool:
    public_key = Path(os.getenv("PUBLIC_KEY_PATH", "keys/public_key.pem"))
    try:
        key = serialization.load_pem_public_key(public_key.read_bytes())
        key.verify(firma, pdf, padding.PKCS1v15(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=f"No se encontró la llave pública: {public_key}") from exc
    except (InvalidKey, ValueError, TypeError) as exc:
        raise HTTPException(status_code=500, detail="La llave pública no es válida") from exc


def _resultado(pdf: bytes, firma: bytes) -> dict:
    return {"resultado": "auténtico" if _verificar(pdf, firma) else "alterado",
            "hash": hashlib.sha256(pdf).hexdigest()}


@router.get("/verificar/{roadmap_id}")
def verificar_por_id(roadmap_id: int):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("""
            SELECT r.archivo_pdf, r.firma, r.hash_sha256, r.emitido_en, u.codigo
            FROM roadmaps_emitidos r JOIN usuarios u ON u.id=r.usuario_id WHERE r.id=%s
        """, (roadmap_id,))
        row = cur.fetchone()
    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="Roadmap no encontrado")
    pdf = bytes(row[0])
    result = _resultado(pdf, bytes(row[1]))
    if result["hash"] != row[2].strip():
        result["resultado"] = "alterado"
    return {**result, "emitido": row[3].isoformat(), "estudiante": row[4]}


@router.post("/verificar")
async def verificar_archivos(documento: UploadFile = File(...), firma: UploadFile = File(...)):
    if documento.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="El documento debe ser un PDF")
    pdf = await documento.read(20 * 1024 * 1024 + 1)
    sig = await firma.read(16 * 1024 + 1)
    if len(pdf) > 20 * 1024 * 1024 or len(sig) > 16 * 1024:
        raise HTTPException(status_code=413, detail="El archivo supera el tamaño permitido")
    if not pdf.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="El archivo seleccionado no parece ser un PDF")
    return _resultado(pdf, sig)
