#!/bin/bash
echo "Generando llaves RSA de 2048 bits..."
openssl genpkey -algorithm RSA -out key/private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in key/private.pem -out key/public.pem
echo "Llaves generadas con exito en la carpeta 'key'."