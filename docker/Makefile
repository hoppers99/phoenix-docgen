# phoenix-docgen Docker image build targets
#
# Usage:
#   make build           Build image locally
#   make build-multiarch Build and push multi-arch image (amd64 + arm64)
#   make push            Push locally built image to GHCR
#   make tag             Show current version tag
#   make clean           Remove local images

IMAGE := ghcr.io/hoppers99/phoenix-docgen
VERSION ?= $(shell cd .. && git describe --tags --always 2>/dev/null || echo "dev")

.PHONY: build build-multiarch push tag clean

build:
	docker build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest ..

build-multiarch:
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t $(IMAGE):$(VERSION) \
		-t $(IMAGE):latest \
		--push ..

push:
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest

tag:
	@echo "$(VERSION)"

clean:
	docker rmi $(IMAGE):$(VERSION) $(IMAGE):latest 2>/dev/null || true
