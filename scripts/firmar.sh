
if [ -z "$1" ]; then
  echo "Error: Debes indicar un archivo. Ejemplo: bash scripts/firmar.sh documento.txt"
  exit 1
fi

echo "Firmando el documento $1..."
openssl dgst -sha256 -sign keys/private.pem -out "$1.sig" "$1"
echo "Firma generada exitosamente: $1.sig"