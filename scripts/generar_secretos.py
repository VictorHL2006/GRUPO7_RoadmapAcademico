"""Genera los secretos para el archivo .env. Copiar las dos líneas a .env (nunca al repositorio)."""
import base64
import secrets

print("ENCRYPTION_KEY=" + base64.b64encode(secrets.token_bytes(32)).decode())
print("JWT_SECRET=" + secrets.token_urlsafe(48))
