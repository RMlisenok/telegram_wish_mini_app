#!/bin/bash

set -e

echo "🚀 Starting SSL certificates initialization..."

# 1. Создаём папки
sudo mkdir -p /opt/ssl/certbot/{conf,www}
sudo chown -R $USER:$USER /opt/ssl

# 2. Останавливаем всё, что мешает
echo "🛑 Stopping services..."
docker-compose down --remove-orphans 2>/dev/null || true
sudo docker stop nginx-temp 2>/dev/null || true
sudo docker rm nginx-temp 2>/dev/null || true
sudo fuser -k 80/tcp 2>/dev/null || true

# 3. Запускаем временный nginx с ПРАВИЛЬНЫМ монтированием
#    Теперь webroot-path и точка монтирования совпадают!
echo "🔄 Starting temporary nginx..."
sudo docker run -d \
  --name nginx-temp \
  -p 80:80 \
  -v /opt/ssl/certbot/www:/var/www/certbot \
  nginx:alpine

# 4. Ждём и проверяем
sleep 5
if ! curl -sSf http://localhost/ > /dev/null; then
    echo "❌ Temporary nginx is not responding"
    sudo docker logs nginx-temp
    exit 1
fi

# 5. Получаем сертификаты (теперь пути совпадают!)
echo "🔐 Obtaining SSL certificates..."
sudo docker run --rm \
  -v /opt/ssl/certbot/conf:/etc/letsencrypt \
  -v /opt/ssl/certbot/www:/var/www/certbot \
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

# 6. Завершаем
echo "🛑 Stopping temporary nginx..."
sudo docker stop nginx-temp && sudo docker rm nginx-temp

echo "✅ Certificates saved in /opt/ssl/certbot/conf/"
sudo chown -R $USER:$USER /opt/ssl