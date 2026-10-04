if [ -z "$1" ]; then
  echo "Error: Debes indicar un archivo. Ejemplo: bash scripts/verificar.sh documento.txt"
  exit 1
fi

echo "Verificando la firma de $1..."
openssl dgst -sha256 -verify keys/public_key.pem -signature "$1.sig" "$1"