.PHONY: help build up down restart logs migrate makemigration shell clean dev

help:
	@echo "Доступные команды:"
	@echo "  make build              - Собрать контейнеры"
	@echo "  make up                 - Запустить контейнеры"
	@echo "  make down               - Остановить контейнеры"
	@echo "  make restart            - Перезапустить контейнеры"
	@echo "  make logs               - Показать логи"
	@echo "  make migrate            - Запустить миграции в контейнере"
	@echo "  make makemigration m=\"message\" - Создать миграцию"
	@echo "  make downgrade          - Откатить последнюю миграцию"
	@echo "  make history            - Показать историю миграций"
	@echo "  make current            - Показать текущую версию"
	@echo "  make shell              - Войти в контейнер backend"
	@echo "  make shell-db           - Войти в базу данных"
	@echo "  make clean              - Очистить всё (контейнеры, volumes)"
	@echo "  make dev                - Собрать, запустить и показать логи"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart: down up

logs:
	docker compose logs -f

dev:
	docker compose up --build

migrate:
	docker compose exec backend uv run alembic upgrade head

makemigration:
	@if [ -z "$(m)" ]; then \
		echo "Ошибка: укажите сообщение: make makemigration m=\"текст\""; \
		exit 1; \
	fi
	cd backend && DB_HOST=localhost DB_PORT=5437 uv run alembic revision --autogenerate -m "$(m)"

downgrade:
	docker compose exec backend uv run alembic downgrade -1

history:
	docker compose exec backend uv run alembic history

current:
	docker compose exec backend uv run alembic current

shell:
	docker compose exec backend bash

shell-db:
	docker compose exec database psql -U postgres -d telegram_app_db

clean:
	docker compose down -v
	rm -rf backend/.venv
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

clean-test:
	cd backend
	rm -rf .pytest_cache
	rm -rf tests/__pycache__
	rm -rf tests/integration/__pycache_