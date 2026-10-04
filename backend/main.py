import os
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Roadmap Académico API")

RUTA_PUBLICA = os.getenv("PUBLIC_KEY_PATH", "keys/public_key.pem")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"estado": "ok"}


@app.post("/verificar")
async def verificar(documento: UploadFile = File(...), firma: UploadFile = File(...)):
    datos = await documento.read()
    sig = await firma.read()

    ruta_publica = Path(RUTA_PUBLICA)
    if not ruta_publica.exists():
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la llave pública en {ruta_publica}",
        )

    try:
        clave = serialization.load_pem_public_key(ruta_publica.read_bytes())
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail="La llave pública no tiene un formato PEM válido.",
        ) from exc

    try:
        clave.verify(sig, datos, padding.PKCS1v15(), hashes.SHA256())
        return {"resultado": "auténtico"}
    except InvalidSignature:
        return {"resultado": "alterado"}