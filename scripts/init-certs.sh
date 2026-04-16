#!/bin/bash

set -e

echo "🚀 Starting SSL certificates initialization..."

# Создаем необходимые директории
mkdir -p certbot/{conf,www}
mkdir -p nginx

echo "📁 Directories created"

# Проверяем наличие конфигов
if [ ! -f nginx/nginx-temp.conf ]; then
    echo "❌ nginx/nginx-temp.conf not found!"
    exit 1
fi

echo "🛑 Stopping all services and cleaning up..."

# Останавливаем все контейнеры
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose -f docker-compose.ssl-init.yml down --remove-orphans 2>/dev/null || true

# Останавливаем и удаляем nginx-temp если он висит
docker stop nginx-temp 2>/dev/null || true
docker rm nginx-temp 2>/dev/null || true

# Удаляем все сети с именем app-network
docker network ls --filter name=app-network -q | xargs -r docker network rm 2>/dev/null || true
docker network ls --filter name=telegram_wish -q | xargs -r docker network rm 2>/dev/null || true

echo "🔄 Starting temporary nginx for certificate issuance..."

# Запускаем временный nginx заново
docker-compose -f docker-compose.ssl-init.yml up -d --remove-orphans

echo "⏳ Waiting for nginx to start..."
sleep 5

# Проверяем что nginx работает
if ! docker ps | grep -q nginx-temp; then
    echo "❌ nginx-temp failed to start"
    docker-compose -f docker-compose.ssl-init.yml logs
    exit 1
fi

echo "🔐 Requesting SSL certificates..."

# Получаем имя сети
NETWORK_NAME=$(docker network ls --filter name=app-network -q | head -1)
if [ -z "$NETWORK_NAME" ]; then
    NETWORK_NAME="telegram_wish_mini_app_app-network"
fi

echo "Using network: $NETWORK_NAME"

# Запускаем certbot
docker run --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  --network "$NETWORK_NAME" \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email skalisusov@inbox.ru \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  --non-interactive \
  -d wishlistprice.ru \
  -d www.wishlistprice.ru

CERTBOT_EXIT=$?

if [ $CERTBOT_EXIT -eq 0 ]; then
    echo "✅ Certificates obtained successfully!"
    
    echo "🛑 Stopping temporary nginx..."
    docker-compose -f docker-compose.ssl-init.yml down
    
    echo "🚀 Starting main services with SSL..."
    docker-compose up -d --remove-orphans
    
    echo "✅ All done! Your site should now be available at https://wishlistprice.ru"
    
    echo "🎉 SSL setup complete!"
else
    echo "❌ Failed to obtain certificates! Exit code: $CERTBOT_EXIT"
    echo "🛑 Stopping temporary nginx..."
    docker-compose -f docker-compose.ssl-init.yml down
    exit 1
fi