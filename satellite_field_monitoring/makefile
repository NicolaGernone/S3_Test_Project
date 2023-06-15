.PHONY: build run test down

build:
	docker-compose build

run:
	docker-compose up

test: build
	docker-compose run app poetry run pytest

down:
	docker-compose down

init: build run
