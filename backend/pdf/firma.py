import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv()
RAIZ = Path(__file__).resolve().parents[2]


def firmar_pdf(pdf: bytes):
    """Devuelve (hash_hex de 64 caracteres, firma de 256 bytes)."""
    hash_hex = hashlib.sha256(pdf).hexdigest()
    ruta = Path(os.getenv("PRIVATE_KEY_PATH", str(RAIZ / "keys" / "private_key.pem")))
    with open(ruta, "rb") as f:
        clave = serialization.load_pem_private_key(f.read(), password=None)
    firma = clave.sign(pdf, padding.PKCS1v15(), hashes.SHA256())
    return hash_hex, firma
