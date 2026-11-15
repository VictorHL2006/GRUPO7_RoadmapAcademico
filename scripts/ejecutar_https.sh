#!/bin/bash
# Backend con TLS (certificado autofirmado de laboratorio). Probar con: curl -k https://localhost:8443/health
uvicorn backend.main:app --port 8443 --ssl-keyfile keys/key.pem --ssl-certfile keys/cert.pem
