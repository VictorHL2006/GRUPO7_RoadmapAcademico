import os
from fastapi import FastAPI, File, UploadFile
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

app = FastAPI(title="Roadmap Académico API")

RUTA_PUBLICA = os.getenv("PUBLIC_KEY_PATH", "keys/public_key.pem")


@app.get("/health")
def health():
    return {"estado": "ok"}


@app.post("/verificar")
async def verificar(documento: UploadFile = File(...), firma: UploadFile = File(...)):
    datos = await documento.read()
    sig = await firma.read()

    with open(RUTA_PUBLICA, "rb") as f:
        clave = serialization.load_pem_public_key(f.read())

    try:
        clave.verify(sig, datos, padding.PKCS1v15(), hashes.SHA256())
        return {"resultado": "auténtico"}
    except InvalidSignature:
        return {"resultado": "alterado"}