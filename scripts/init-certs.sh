#!/bin/bash

echo "🚀 Starting SSL certificates initialization..."

# Создаём папки
mkdir -p /home/runner/ssl/certbot/{conf,www}

echo "🛑 Stopping all services (особенно nginx)..."
docker-compose down --remove-orphans 2>/dev/null || true
docker stop nginx-temp 2>/dev/null || true
docker rm nginx-temp 2>/dev/null || true

# Убиваем процесс на порту 80 (если что-то ещё висит)
sudo fuser -k 80/tcp 2>/dev/null || true

echo "🔄 Starting temporary nginx with correct config..."
docker run -d \
  --name nginx-temp \
  -p 80:80 \
  -v /home/runner/ssl/certbot/www:/var/www/certbot \
  nginx:alpine

sleep 5

# Проверка, что nginx отвечает
if ! curl -sSf http://localhost/ > /dev/null; then
    echo "❌ Temporary nginx is not responding"
    docker logs nginx-temp
    exit 1
fi

echo "🔐 Obtaining SSL certificates..."
docker run --rm \
  -v /home/runner/ssl/certbot/conf:/etc/letsencrypt \
  -v /home/runner/ssl/certbot/www:/var/www/certbot \
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
docker stop nginx-temp && docker rm nginx-temp

echo "✅ Done! Certificates in /home/runner/ssl/certbot/conf/"