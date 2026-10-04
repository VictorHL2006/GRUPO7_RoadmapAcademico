echo "Generando certificado TLS autofirmado..."
openssl req -x509 -new -nodes -key key/private.pem -sha256 -days 365 -out key/certificado.crt -subj "/C=PE/ST=Arequipa/L=Arequipa/O=Grupo7/CN=roadmapacademico.local"
echo "Certificado generado exitosamente: key/certificado.crt"