DOCKER_IMAGE=pocket-wiki
DOCKER_CONTAINER=pocket-wiki
DOCKER_NET=static
DOCKER_IP=172.18.0.5
UID=$(shell ls -ldn instance | cut -d' ' -f3)

all: pull build restart

pull:
	git pull

build:
	docker build --build-arg uid=$(UID) --tag $(DOCKER_IMAGE) .

build-no-cache:
	docker build --no-cache --build-arg uid=$(UID) --tag $(DOCKER_IMAGE) .

debug:
	docker run --rm -it \
		--name $(DOCKER_CONTAINER) \
		-v `pwd`/instance:/app/instance \
		$(DOCKER_IMAGE)

start:
	docker run --name $(DOCKER_CONTAINER) \
		-d --restart=always \
		--net $(DOCKER_NET) --ip $(DOCKER_IP) \
		-v `pwd`/instance:/app/instance \
		$(DOCKER_IMAGE)

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

