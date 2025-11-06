# Nicholas J Uhlhorn
# November 2025

IMAGE_NAME := flask-app-docker
CONTAINER_NAME := flask-app-container

.PHONY: all build run stop clean help

all: build run

build:
	@echo "=========================================="
	@echo "  Building Docker image: $(IMAGE_NAME)"
	@echo "=========================================="
	docker build -t $(IMAGE_NAME) .

run: stop
	@echo "=========================================="
	@echo "  Starting server on http://localhost:5000"
	@echo "=========================================="

	docker run -p 5000:5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)
	@echo "Server started successfully. Container ID: $$(docker ps -q -f name=$(CONTAINER_NAME))"
	@echo "Use 'make stop' to shut it down."

detatched: stop 
	@echo "=========================================="
	@echo "     Starting server (non-detatched)"
	@echo "=========================================="

	docker run -d -p 5000:5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)
	@echo "Server started successfully. Container ID: $$(docker ps -q -f name=$(CONTAINER_NAME))"
	@echo "Use 'make stop' to shut it down."

stop:
	@echo "=========================================="
	@echo "  Attempting to stop and remove container $(CONTAINER_NAME)..."
	@echo "=========================================="

	-docker stop $(CONTAINER_NAME) 2> /dev/null || true
	-docker rm $(CONTAINER_NAME) 2> /dev/null || true
	@echo "Container cleanup complete."

clean: stop
	@echo "=========================================="
	@echo "  Removing Docker image $(IMAGE_NAME)..."
	@echo "=========================================="

	-docker rmi $(IMAGE_NAME) 2> /dev/null || true
	@echo "Image cleanup complete."

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@echo "  all     : Runs 'build' then 'run' (default)."
	@echo "  build   : Builds the Docker image ($(IMAGE_NAME))."
	@echo "  run     : Stops existing container, then runs the image and maps port 5000."
	@echo "  stop    : Stops and removes the running container ($(CONTAINER_NAME))."
	@echo "  clean   : Stops/removes the container and removes the Docker image."
