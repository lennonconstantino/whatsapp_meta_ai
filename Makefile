.PHONY: help run stop restart migrate seed

help:
	@echo "Available commands:"
	@echo "  make run              - Run the application"
	@echo "  make help             - Show this help message"

run:
	@echo "Starting application in background (logs -> app.log)..."
	FORCE_COLOR=true python -m src.main >> app.log 2>&1 &
	@echo "✅ Application is running."
	@echo "-> see logs: tail -f app.log"

stop:
	@echo "Stopping application and workers..."
	@-pkill -f "python -m src.main"
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