#!/bin/bash

# НЕ используем sudo
echo "🚀 Starting SSL certificates initialization..."

mkdir -p certbot/{conf,www}
mkdir -p nginx

# Убеждаемся что права правильные
chmod -R 755 certbot

echo "🛑 Stopping services..."
docker-compose down --remove-orphans 2>/dev/null || true

echo "🔄 Starting temporary nginx..."
docker run -d \
  --name nginx-temp \
  -p 80:80 \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -v $(pwd)/nginx/nginx-temp.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine

sleep 5

echo "🔐 Obtaining SSL certificates..."
docker run --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  --network host \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email skalisusov@inbox.ru \
  --agree-tos \
  --no-eff-email \
  --non-interactive \
  -d wishlistprice.ru \
  -d www.wishlistprice.ru

echo "🛑 Stopping temporary nginx..."
docker stop nginx-temp
docker rm nginx-temp

# Меняем владельца на runner (если файлы создались от root)
chown -R runner:runner certbot/conf 2>/dev/null || true

echo "✅ Done!"