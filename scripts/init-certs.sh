#!/bin/bash

echo "🚀 Starting SSL certificates initialization..."

# Создаем директории в HOME runner
mkdir -p /home/runner/ssl/certbot/{conf,www}

echo "🛑 Stopping services..."
docker-compose down --remove-orphans 2>/dev/null || true

# Останавливаем временный nginx
docker stop nginx-temp 2>/dev/null || true
docker rm nginx-temp 2>/dev/null || true

echo "🔄 Starting temporary nginx..."
docker run -d \
  --name nginx-temp \
  -p 80:80 \
  -v /home/runner/ssl/certbot/www:/var/www/certbot \
  nginx:alpine

sleep 5

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
docker stop nginx-temp
docker rm nginx-temp

echo "✅ Certificates saved in /home/runner/ssl/certbot/conf/"