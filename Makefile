# Flujo de trabajo climachile. Mismos comandos en la nube y en el laptop.
#   make setup              entorno Python (uv) + R (renv)
#   make r-actualizar       tras agregar un paquete R a DESCRIPTION
#   make doctor             revisa herramientas y acceso a Drive
#   make pull RUTA=marts/x  baja datos desde Drive a la caché local
#   make push RUTA=raw/x    sube datos a Drive y actualiza el manifiesto
#   make ls [RUTA=raw]      lista lo que hay en Drive
#   make check              lint + tests

UV ?= uv
CLI = $(UV) run --quiet climachile

.PHONY: help setup setup-py setup-r r-actualizar doctor pull push push-forzar ls verificar lint test check

help:
	@grep -E '^#' Makefile | sed 's/^# \{0,1\}//'

setup: setup-py setup-r

setup-py:
	$(UV) sync

setup-r:
	Rscript R/setup.R

# Tras agregar un paquete a DESCRIPTION: lo instala y actualiza renv.lock.
r-actualizar:
	Rscript -e 'renv::install(prompt = FALSE); renv::snapshot(prompt = FALSE)'

doctor:
	@$(CLI) doctor

pull:
	@test -n "$(RUTA)" || (echo "Uso: make pull RUTA=marts/<tabla>"; exit 2)
	$(CLI) pull "$(RUTA)"

push:
	@test -n "$(RUTA)" || (echo "Uso: make push RUTA=raw/<fuente>"; exit 2)
	$(CLI) push "$(RUTA)"

push-forzar:
	@test -n "$(RUTA)" || (echo "Uso: make push-forzar RUTA=raw/<fuente>"; exit 2)
	$(CLI) push --forzar "$(RUTA)"

ls:
	@$(CLI) ls $(RUTA)

verificar:
	@test -n "$(RUTA)" || (echo "Uso: make verificar RUTA=raw/<fuente>"; exit 2)
	$(CLI) verificar "$(RUTA)"

lint:
	$(UV) run ruff check src tests

test:
	$(UV) run pytest -q

check: lint test
