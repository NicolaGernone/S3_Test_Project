.PHONY: build run test down

build:
	docker-compose build

up:
	docker-compose up

test: build
	docker-compose run app poetry run pytest

down:
	docker-compose down

run: build run
