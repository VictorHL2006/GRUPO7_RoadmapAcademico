#!/bin/bash
# Uso: bash scripts/firmar.sh documento.pdf
openssl dgst -sha256 -sign keys/private_key.pem -out "$1.sig" "$1"
echo "Firma creada: $1.sig"
