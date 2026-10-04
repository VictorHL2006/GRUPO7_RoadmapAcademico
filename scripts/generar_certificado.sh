mkdir -p keys
echo "Generando certificado TLS autofirmado..."
openssl req -x509 -new -nodes -key keys/private.pem -sha256 -days 365 -out keys/cert.pem -subj "/C=PE/ST=Arequipa/L=Arequipa/O=Grupo7/CN=roadmapacademico.local"
echo "Certificado generado exitosamente: keys/cert.pem"