DOCKER_IMAGE=pocket-wiki
DOCKER_CONTAINER=$(shell ./docker-options --docker-container)
UID=$(shell ls -ldn instance | cut -d' ' -f3)

all: pull build restart

pull:
	git pull

build:
	test -d instance || mkdir instance
	docker build --build-arg uid=$(UID) --tag $(DOCKER_IMAGE) .

build-no-cache:
	docker build --no-cache --build-arg uid=$(UID) --tag $(DOCKER_IMAGE) .

debug:
	docker run --rm -it $(shell ./docker-options) $(DOCKER_IMAGE) ./start.py --debug

start:
	docker run --detach --restart=always $(shell ./docker-options) $(DOCKER_IMAGE)

stop:
	docker stop $(DOCKER_CONTAINER)
	docker rm $(DOCKER_CONTAINER)

restart: stop start

shell:
	docker exec -it $(DOCKER_CONTAINER) /bin/sh

logs:
	docker logs $(DOCKER_CONTAINER) 2>&1

tail:
	docker logs -f $(DOCKER_CONTAINER) 2>&1

