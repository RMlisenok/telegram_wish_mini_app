#!/bin/bash

echo "🚀 Starting SSL certificates initialization..."

# Создаём папки в проекте (для временного nginx)
mkdir -p certbot/conf certbot/www
mkdir -p /home/runner/ssl/certbot/{conf,www}

echo "🛑 Stopping all services..."
docker-compose down --remove-orphans 2>/dev/null || true
docker stop nginx-temp 2>/dev/null || true
docker rm nginx-temp 2>/dev/null || true

echo "🔄 Starting temporary nginx with your config..."
# Используем docker-compose для запуска временного nginx с правильным конфигом
docker-compose -f docker-compose.ssl-init.yml up -d

sleep 5

# Проверка, что nginx отвечает
if ! curl -sSf http://localhost/ > /dev/null; then
    echo "❌ Temporary nginx is not responding"
    docker logs nginx-temp
    exit 1
fi

echo "🔐 Obtaining SSL certificates..."
# Сначала пробуем получить в /home/runner/ssl
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
docker-compose -f docker-compose.ssl-init.yml down

if [ $CERTBOT_EXIT -eq 0 ]; then
    echo "✅ Certificates saved in /home/runner/ssl/certbot/conf/"
    
    # Копируем сертификаты в проект (для резервной копии)
    cp -r /home/runner/ssl/certbot/conf/* certbot/conf/ 2>/dev/null || true
    
    # Проверяем
    if [ -f /home/runner/ssl/certbot/conf/live/wishlistprice.ru/fullchain.pem ]; then
        echo "✅ Certificate files verified"
        ls -la /home/runner/ssl/certbot/conf/live/wishlistprice.ru/
    fi
else
    echo "❌ Failed to obtain certificates!"
    exit 1
fi