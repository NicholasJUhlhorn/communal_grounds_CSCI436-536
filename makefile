# Nicholas J Uhlhorn
# November 2025

# Define the service name from docker-compose.yaml

SERVICE_NAME := web

.PHONY: all build run logs stop clean help

all: run

build:
	@echo "=========================================="
	@echo "  Building Docker Compose services..."
	@echo "=========================================="
	# Use docker-compose build to build the image defined in docker-compose.yaml
	docker-compose build

run:
	@echo "=========================================="
	@echo "  Starting server on http://localhost:5000"
	@echo "=========================================="
	# 'docker-compose up' handles building, volume mapping, port mapping, and running
	# It also correctly uses the SQLite volume mapping from docker-compose.yaml.
	docker-compose up 
	@echo "Server started successfully."
	@echo "Use 'make logs' to view output or 'make stop' to shut it down."

# We'll use 'run' as the default detached start and remove the older 'detatched' target

logs:
	@echo "=========================================="
	@echo "  Viewing logs for $(SERVICE_NAME)..."
	@echo "=========================================="
	docker-compose logs -f

stop:
	@echo "=========================================="
	@echo "  Attempting to stop and remove service..."
	@echo "=========================================="
	# Use 'docker-compose down' to stop the service and remove the containers/networks
	-docker-compose down 2> /dev/null || true
	@echo "Container cleanup complete."

clean: stop
	@echo "=========================================="
	@echo "  Removing Docker images..."
	@echo "=========================================="
	# Remove the images created by the compose file
	-docker-compose rm -s -f -v 2> /dev/null || true
	# Assuming your image tag is set by the compose file build context.
	# A clean 'docker-compose down -v --rmi all' is generally safer, but keeping close to your original logic:
	-docker rmi $(shell docker images -qf "label=com.docker.compose.project") 2> /dev/null || true
	@echo "Image cleanup complete."

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@echo "  all     : Runs 'run' (default), which starts the server detached."
	@echo "  build   : Builds the Docker image."
	@echo "  run     : Builds and starts the service in detached mode (-d)."
	@echo "  logs    : Follows the logs of the running container."
	@echo "  stop    : Stops and removes the container."
	@echo "  clean   : Stops/removes the container and removes the Docker image."
