.PHONY: install lint test run-api scan history

install:
	python3 -m poetry install

lint:
	python3 -m poetry run ruff check src tests

test:
	python3 -m poetry run pytest

run-api:
	python3 -m poetry run reputation-pulse api

scan:
	python3 -m poetry run reputation-pulse scan g-dos

history:
	python3 -m poetry run reputation-pulse history --limit 20
