#!/bin/bash

echo "🚀 Starting SSL certificates initialization..."

# Создаём папки
mkdir -p /home/runner/ssl/certbot/{conf,www}

echo "🛑 Stopping all services (особенно nginx)..."
docker-compose down --remove-orphans 2>/dev/null || true
docker stop nginx-temp 2>/dev/null || true
docker rm nginx-temp 2>/dev/null || true

# Проверяем, что порт 80 свободен
if docker ps | grep -q ":80->"; then
    echo "⚠️ Port 80 is still busy. Stopping remaining containers..."
    docker stop $(docker ps | grep ":80->" | awk '{print $1}') 2>/dev/null || true
fi

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

CERTBOT_EXIT=$?

echo "🛑 Stopping temporary nginx..."
docker stop nginx-temp && docker rm nginx-temp

if [ $CERTBOT_EXIT -eq 0 ]; then
    echo "✅ Certificates saved in /home/runner/ssl/certbot/conf/"
    
    # Проверяем, что сертификаты созданы
    if [ -f /home/runner/ssl/certbot/conf/live/wishlistprice.ru/fullchain.pem ]; then
        echo "✅ Certificate files verified"
        ls -la /home/runner/ssl/certbot/conf/live/wishlistprice.ru/
    fi
else
    echo "❌ Failed to obtain certificates!"
    echo "Check that your domain DNS resolves to this server"
    echo "And that port 80 is accessible from internet"
    exit 1
fi