import hashlib
import hmac
import os
from pathlib import Path
from urllib.parse import quote

from cryptography.exceptions import InvalidKey, InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

from backend.db import get_conn

router = APIRouter(tags=["verificación"])
MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_SIGNATURE_BYTES = 16 * 1024
RAIZ = Path(__file__).resolve().parents[2]


def _verificar(pdf: bytes, firma: bytes) -> bool:
    public_key = Path(os.getenv("PUBLIC_KEY_PATH", str(RAIZ / "keys" / "public_key.pem")))
    try:
        key = serialization.load_pem_public_key(public_key.read_bytes())
        key.verify(firma, pdf, padding.PKCS1v15(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail="No se encontró la llave pública configurada") from exc
    except (InvalidKey, ValueError, TypeError) as exc:
        raise HTTPException(status_code=500, detail="La llave pública no es válida") from exc


def _resultado(pdf: bytes, firma: bytes) -> dict:
    return {"resultado": "auténtico" if _verificar(pdf, firma) else "alterado",
            "hash": hashlib.sha256(pdf).hexdigest()}


def _leer_codigo(codigo: str):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute(
            """SELECT r.archivo_pdf, r.firma, r.hash_sha256, r.emitido_en,
                      u.codigo, r.codigo_verificacion
               FROM roadmaps_emitidos r JOIN usuarios u ON u.id=r.usuario_id
               WHERE r.id::text=%s OR r.codigo_verificacion::text=%s""",
            (codigo, codigo),
        )
        return cur.fetchone()


def _detalle_verificacion(codigo: str):
    row = _leer_codigo(codigo)
    if not row or row[0] is None:
        raise HTTPException(status_code=404, detail="Roadmap no encontrado")
    pdf, firma, hash_guardado, emitido, estudiante, codigo_uuid = row
    resultado = _resultado(bytes(pdf), bytes(firma))
    if not hmac.compare_digest(resultado["hash"], hash_guardado.strip()):
        resultado["resultado"] = "alterado"
    return {**resultado, "codigo": str(codigo_uuid), "emitido": emitido.isoformat(),
            "estudiante": estudiante}


async def _recibir_pdf(documento: UploadFile) -> bytes:
    if documento.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="El documento debe ser un PDF")
    pdf = await documento.read(MAX_PDF_BYTES + 1)
    if len(pdf) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="El PDF supera el tamaño permitido")
    if not pdf.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="El archivo seleccionado no parece ser un PDF")
    return pdf


@router.get("/verificar/{codigo}")
def verificar_por_codigo(codigo: str):
    return _detalle_verificacion(codigo)


@router.get("/v/{codigo}")
def abrir_verificacion(codigo: str):
    frontend = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
    return RedirectResponse(f"{frontend}/verificar.html?codigo={quote(codigo, safe='')}", status_code=307)


@router.post("/verificar")
async def verificar_archivos(documento: UploadFile = File(...), firma: UploadFile = File(...)):
    pdf = await _recibir_pdf(documento)
    sig = await firma.read(MAX_SIGNATURE_BYTES + 1)
    if len(sig) > MAX_SIGNATURE_BYTES:
        raise HTTPException(status_code=413, detail="La firma supera el tamaño permitido")
    return _resultado(pdf, sig)


@router.post("/verificar/{codigo}/documento")
async def verificar_documento_emitido(codigo: str, documento: UploadFile = File(...)):
    pdf = await _recibir_pdf(documento)
    row = _leer_codigo(codigo)
    if not row or row[0] is None:
        raise HTTPException(status_code=404, detail="Roadmap no encontrado")

    guardado, firma, hash_guardado, emitido, estudiante, codigo_uuid = row
    hash_subido = hashlib.sha256(pdf).hexdigest()
    autentic = (
        hmac.compare_digest(hash_subido, hash_guardado.strip())
        and _verificar(pdf, bytes(firma))
        and hmac.compare_digest(pdf, bytes(guardado))
    )
    return {
        "resultado": "auténtico" if autentic else "alterado",
        "codigo": str(codigo_uuid),
        "hash": hash_subido,
        "emitido": emitido.isoformat(),
        "estudiante": estudiante,
    }
