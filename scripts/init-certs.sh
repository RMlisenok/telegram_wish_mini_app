#!/bin/bash

set -e

echo "🚀 FIRST TIME SSL CERTIFICATES SETUP"

# Создаем необходимые директории
mkdir -p certbot/{conf,www}
mkdir -p nginx

echo "🛑 Stopping all services..."
sudo docker-compose down --remove-orphans 2>/dev/null || true

echo "🔄 Starting temporary nginx..."
sudo docker run -d \
  --name nginx-temp \
  -p 80:80 \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -v $(pwd)/nginx/nginx-temp.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine

sleep 5

echo "🔐 Obtaining SSL certificates (this happens only once)..."
sudo docker run --rm \
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
sudo docker stop nginx-temp
sudo docker rm nginx-temp

echo "✅ SSL certificates obtained and saved in certbot/conf/"
echo "These certificates will be automatically renewed by certbot container"