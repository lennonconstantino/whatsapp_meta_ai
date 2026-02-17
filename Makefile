.PHONY: help run stop restart migrate seed

help:
	@echo "Available commands:"
	@echo "  make run              - Run the application"
	@echo "  make help             - Show this help message"

run:
	@echo "Starting application in background (logs -> app.log)..."
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --debug >> app.log 2>&1 &
	@echo "✅ Application is running."
	@echo "-> see logs: tail -f app.log

stop:
	@echo "Stopping application and workers..."
	@-pkill -f "uvicorn src.main:app"
	@echo "✅ Application and workers stopped."

restart: stop run
	@echo "✅ Application restarted."

migrate:
	@echo "Running database migrations..."
	@python -m scripts.database.migrate
	@echo "✅ Database migrations completed."

seed:
	@echo "Seeding database..."
	@python -m scripts.database.seed_meta
	@echo "✅ Database seeded."