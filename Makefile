APP=media-translator
SERVICE=api
CONTAINER=media-translator

build:
	docker compose build

dev:
	docker compose up

ssh:
	# enter as webapp user
	docker exec -it -u webapp $(CONTAINER) bash

stop:
	docker compose down -v
