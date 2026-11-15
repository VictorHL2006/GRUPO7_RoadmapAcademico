#!/bin/bash
mkdir -p keys
openssl genrsa -out keys/private_key.pem 2048
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem
chmod 600 keys/private_key.pem
echo "Llaves generadas en keys/"
