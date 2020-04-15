DOCKER_IMAGE = openmaraude/minimal_operateur_server

all:
	@echo "To build and push Docker image, run make release"

release:
	docker build -t ${DOCKER_IMAGE}:latest .
	docker push ${DOCKER_IMAGE}:latest
