.PHONY: help build up up-build down down-v restart ps logs logs-api logs-db logs-mail makemigrations migrate superuser collectstatic shell dbshell black black-check black-diff clean

ifneq ("$(wildcard local.yml)","")
DC := docker compose -f local.yml
else
DC := docker compose -f api/local.yml --project-directory api
endif

help:
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start containers in detached mode"
	@echo "  make up-build       - Build and start containers in detached mode"
	@echo "  make down           - Stop and remove containers"
	@echo "  make down-v         - Stop and remove containers along with volumes"
	@echo "  make restart        - Restart all containers"
	@echo "  make ps             - View container status"
	@echo "  make logs           - Follow logs for all services"
	@echo "  make logs-api       - Follow Django API logs"
	@echo "  make logs-db        - Follow PostgreSQL logs"
	@echo "  make logs-mail      - Follow Mailpit logs"
	@echo "  make makemigrations - Create new Django migrations"
	@echo "  make migrate        - Run database migrations"
	@echo "  make superuser      - Create a Django superuser"
	@echo "  make collectstatic  - Collect static files"
	@echo "  make shell          - Open Django interactive shell"
	@echo "  make dbshell        - Open PostgreSQL psql shell"
	@echo "  make black          - Format Python code with Black"
	@echo "  make black-check    - Check formatting with Black"
	@echo "  make black-diff     - Show Black formatting diff"
	@echo "  make clean          - Remove Python bytecode and cache files"

build:
	$(DC) build

up:
	$(DC) up -d

up-build:
	$(DC) up --build -d --remove-orphans

down:
	$(DC) down

down-v:
	$(DC) down -v

restart:
	$(DC) restart

ps:
	$(DC) ps

logs:
	$(DC) logs -f

logs-api:
	$(DC) logs -f api

logs-db:
	$(DC) logs -f postgres

logs-mail:
	$(DC) logs -f mailpit

makemigrations:
	$(DC) exec api python manage.py makemigrations

migrate:
	$(DC) exec api python manage.py migrate

superuser:
	$(DC) exec api python manage.py createsuperuser

collectstatic:
	$(DC) exec api python manage.py collectstatic --no-input --clear

shell:
	$(DC) exec api python manage.py shell

dbshell:
	$(DC) exec postgres psql -U postgres -d banker

black:
	$(DC) exec api black .

black-check:
	$(DC) exec api black --check .

black-diff:
	$(DC) exec api black --diff .

clean:
	python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
