# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Используем простой сервер для статики
FROM node:20-alpine

WORKDIR /app

# Копируем собранное приложение
COPY --from=builder /app/dist ./dist

# Устанавливаем serve для статики
RUN npm install -g serve

# Health check endpoint
RUN echo '{"status": "healthy", "service": "frontend"}' > ./health.json

EXPOSE 80

# Запускаем сервер
CMD ["serve", "-s", "dist", "-l", "80"]