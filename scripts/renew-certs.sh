#!/bin/bash

echo "🔄 Manually renewing SSL certificates..."

sudo docker run --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot renew \
  --webroot -w /var/www/certbot \
  --quiet

echo "🔄 Reloading nginx..."
sudo docker-compose exec nginx nginx -s reload

echo "✅ Certificate renewal completed"