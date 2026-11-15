#!/bin/bash
mkdir -p keys
openssl req -x509 -newkey rsa:2048 -nodes -keyout keys/key.pem \
  -out keys/cert.pem -days 365 -subj "/CN=localhost"
chmod 600 keys/key.pem
echo "Certificado de prueba generado en keys/"
