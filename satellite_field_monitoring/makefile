.PHONY: build run test down

build:
	docker-compose build

up:
	docker-compose up

test: build
	docker-compose run pytest

down:
	docker-compose down

requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

env:
	conda activate env

update_env:
	conda update env

run: build up

add:
	poetry add $(pkg)
	@make requirements
	@make update_env