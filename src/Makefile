all: build

help:
	@echo ""
	@echo "-- Help Menu"
	@echo ""
	@echo "   1. make build        - build the gaia-downloader image"
	@echo "   2. make quickstart   - start a db instance and begin to download stars"
	@echo "   3. make stop         - stop gaia downloader"
	@echo "   4. make remove       - remove all containers
	@echo "   4. make log          - view log"

build:
	@docker build --tag=ghcr.io/cdalvaro/gaia-downloader:latest \
		--file downloader.Dockerfile .

quickstart:
	@echo "Starting DB and gaia-downloader containers..."
	@docker-compose up --detach
	@echo "Type 'make log' for the log"

stop:
	@echo "Stopping container..."
	@docker-compose stop downloader

remove:
	@echo "Removing containers..."
	@docker-compose down

log:
	@docker-compose logs --follow
