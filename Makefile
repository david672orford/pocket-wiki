NAME=pocket-wiki
DOCKER_NET=static
DOCKER_IP=172.18.0.5

all: pull build restart

pull:
	git pull

build:
	docker build -t $(NAME) .

build-no-cache:
	docker build --no-cache -t $(NAME) .

debug:
	docker run --rm -it \
		--name $(NAME)_debug \
		-v `pwd`/instance:/app/instance \
		$(NAME)

shell:
	docker exec -it $(NAME)_prod /bin/sh

start:
	docker run --name $(NAME)_prod \
		-d --restart=always \
		--net $(DOCKER_NET) --ip $(DOCKER_IP) \
		-v `pwd`/instance:/app/instance \
		-p 5000:5000/udp \
		$(NAME)

stop:
	docker stop $(NAME)_prod
	docker rm $(NAME)_prod

restart: stop start

logs:
	docker logs $(NAME)_prod

tail:
	docker logs -f $(NAME)_prod

