
mkdir -p ssl

openssl genrsa -out ssl/nginx.key 2048

openssl req -new -x509 -key ssl/nginx.key -out ssl/nginx.crt -days 365 -subj "/C=RU/ST=State/L=City/O=Organization/CN=localhost"

chmod 600 ssl/nginx.key
chmod 644 ssl/nginx.crt

echo "SSL сертификат создан в директории ssl/"
