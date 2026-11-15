#!/bin/bash
# Uso: bash scripts/verificar.sh documento.pdf   (usa documento.pdf.sig)
openssl dgst -sha256 -verify keys/public_key.pem -signature "$1.sig" "$1"
