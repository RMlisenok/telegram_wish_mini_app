#!/bin/bash

set -e

echo "Starting SSL certificates initialization..."

# Создаем необходимые директории
mkdir -p certbot/{conf,www}
mkdir -p nginx

echo "Directories created"

# Проверяем наличие конфигов
if [ ! -f nginx/nginx-temp.conf ]; then
    echo "nginx/nginx-temp.conf not found!"
    exit 1
fi

echo "Stopping main services if running..."
docker-compose down

echo "Starting temporary nginx for certificate issuance..."
docker-compose -f docker-compose.ssl-init.yml up -d

echo "Waiting for nginx to start..."
sleep 5

echo "Requesting SSL certificates..."
docker run --rm \
  --name certbot-generate \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  --network telegram_wish_mini_app_app-network \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email skalisusov@inbox.ru \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  -d wishlistprice.ru \
  -d www.wishlistprice.ru

if [ $? -eq 0 ]; then
    echo "Certificates obtained successfully!"
    
    echo "Stopping temporary nginx..."
    docker-compose -f docker-compose.ssl-init.yml down
    
    echo "Starting main services with SSL..."
    docker-compose up -d
    
    echo "All done! Your site should now be available at https://wishlistprice.ru"
    
    # Проверяем что certbot renew работает
    echo "Testing certbot renewal..."
    docker run -it --rm \
      -v $(pwd)/certbot/conf:/etc/letsencrypt \
      -v $(pwd)/certbot/www:/var/www/certbot \
      certbot/certbot renew --dry-run
    
    echo "SSL setup complete!"
else
    echo "Failed to obtain certificates!"
    echo "Stopping temporary nginx..."
    docker-compose -f docker-compose.ssl-init.yml down
    exit 1
fi