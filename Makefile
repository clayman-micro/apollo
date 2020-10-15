.PHONY: build clean clean-test clean-pyc clean-build proto
NAME	:= ghcr.io/clayman-micro/apollo
VERSION ?= latest


clean: clean-build clean-image clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-image:
	docker images -qf dangling=true | xargs docker rmi

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr tests/coverage
	rm -f tests/coverage.xml

install: clean
	poetry install

lint:
	poetry run flake8 src/apollo tests
	poetry run mypy src/apollo tests

run:
	poetry run python3 -m apollo --conf-dir=./conf --debug server run -t develop -t 'traefik.enable=true' -t 'traefik.http.routers.apollo.rule=Host(`apollo.dev.clayman.pro`)' -t 'traefik.http.routers.apollo.entrypoints=web' -t 'traefik.http.routers.apollo.service=apollo' -t 'traefik.http.routers.apollo.middlewares=apollo-redirect@consulcatalog' -t 'traefik.http.routers.apollo-secure.rule=Host(`apollo.dev.clayman.pro`)' -t 'traefik.http.routers.apollo-secure.entrypoints=websecure' -t 'traefik.http.routers.apollo-secure.service=apollo' -t 'traefik.http.routers.apollo-secure.tls=true' -t 'traefik.http.middlewares.apollo-redirect.redirectscheme.scheme=https' -t 'traefik.http.middlewares.apollo-redirect.redirectscheme.permanent=true'

test:
	tox

dist: clean-build
	poetry build

build:
	docker build -t ${NAME} .
	docker tag ${NAME} ${NAME}:$(VERSION)

publish:
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS)
	docker push ${NAME}:$(VERSION)
