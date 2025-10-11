PROJECT_NAME=openproject

.PHONY: run up migrate down logs restart

up:
	docker compose -p $(PROJECT_NAME) up -d
	@echo "Waiting for database to be ready..."
	sleep 30
	@echo "Running database migrations and seed..."
	docker compose run --rm openproject bash -c "RAILS_ENV=production bundle exec rake db:migrate db:seed"

down:
	docker compose -p $(PROJECT_NAME) down -v

restart:
	docker compose -p $(PROJECT_NAME) down
	docker compose -p $(PROJECT_NAME) up -d

kill:
	$(MAKE) down
	$(MAKE) up