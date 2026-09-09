.DEFAULT_GOAL := help

PYTHON ?= python
COMPOSE := docker compose -f infra/docker-compose.yaml
SERVICE ?=
TAIL ?= 100

.PHONY: help validate setup build run restart-apps stop status logs \
	install-scripts count count-watch unit-tests

help:
	@echo "make setup          Valida, descarga imágenes y construye"
	@echo "make build          Reconstruye las imágenes Python"
	@echo "make run            Levanta todos los servicios"
	@echo "make restart-apps   Reinicia emitter y receptores"
	@echo "make stop           Detiene todos los servicios"
	@echo "make status         Muestra el estado de los contenedores"
	@echo "make logs           Sigue los logs de todos los servicios"
	@echo "make logs SERVICE=receptor TAIL=50"
	@echo "make install-scripts Instala las dependencias de los scripts"
	@echo "make validate       Valida el archivo Compose"
	@echo "make count          Muestra el conteo de IPs únicas"
	@echo "make count-watch    Observa el conteo de IPs únicas"
	@echo "make unit-tests     Ejecuta las pruebas unitarias"

validate:
	$(COMPOSE) config --quiet

setup: validate
	$(COMPOSE) pull kafka kafka-init redis
	$(COMPOSE) build emitter receptor

build: validate
	$(COMPOSE) build emitter receptor

run: validate
	$(COMPOSE) up -d

restart-apps:
	$(COMPOSE) restart emitter receptor

stop:
	$(COMPOSE) stop

status:
	$(COMPOSE) ps -a

logs:
	$(COMPOSE) logs --follow --tail=$(TAIL) $(SERVICE)

install-scripts:
	$(PYTHON) -m pip install -r scripts/requirements.txt

count: install-scripts
	$(PYTHON) scripts/get_count.py

count-watch: install-scripts
	$(PYTHON) scripts/get_count.py --watch

install-unit-tests:
	$(PYTHON) -m pip install -r test/unit/requirements.txt

unit-tests: install-unit-tests
	$(PYTHON) -m pytest -v -s test/unit