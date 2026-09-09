.DEFAULT_GOAL := help

PYTHON ?= python
COMPOSE := docker compose -f infra/docker-compose.yaml
SERVICE ?=
TAIL ?= 100

.PHONY: help install-emitter install-receptor install-all \
	validate setup build run restart-apps stop status logs count

help:
	@echo "make setup          Valida, descarga imagenes y construye"
	@echo "make build          Reconstruye las imagenes Python"
	@echo "make run            Levanta todos los servicios"
	@echo "make restart-apps   Reinicia emitter y receptores"
	@echo "make stop           Detiene todos los servicios"
	@echo "make status         Muestra el estado de los contenedores"
	@echo "make logs           Sigue los logs de todos los servicios"
	@echo "make logs SERVICE=receptor TAIL=50"
	@echo "make install-scripts Instala las dependencias de los scripts"
	@echo "make validate       Valida el archivo Compose"
	@echo "make count          Muestra el conteo de IPs únicas"

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