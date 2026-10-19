import hashlib
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv()


def firmar_pdf(pdf: bytes):
    """Devuelve (hash_hex de 64 caracteres, firma de 256 bytes)."""
    hash_hex = hashlib.sha256(pdf).hexdigest()
    ruta = os.getenv("PRIVATE_KEY_PATH", "keys/private.pem")
    with open(ruta, "rb") as f:
        clave = serialization.load_pem_private_key(f.read(), password=None)
    firma = clave.sign(pdf, padding.PKCS1v15(), hashes.SHA256())
    return hash_hex, firma
