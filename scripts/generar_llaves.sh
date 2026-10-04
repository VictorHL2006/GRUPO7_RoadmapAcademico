#!/bin/bash
mkdir -p keys
echo "Generando llaves RSA de 2048 bits..."
openssl genpkey -algorithm RSA -out keys/private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in keys/private.pem -out keys/public_key.pem
echo "Llaves generadas con éxito en la carpeta 'keys'."