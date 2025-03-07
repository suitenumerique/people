# /!\ /!\ /!\ /!\ /!\ /!\ /!\ DISCLAIMER /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
#
# This Makefile is only meant to be used for DEVELOPMENT purpose as we are
# changing the user id that will run in the container.
#
# PLEASE DO NOT USE IT FOR YOUR CI/PRODUCTION/WHATEVER...
#
# /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
#
# Note to developers:
#
# While editing this file, please respect the following statements:
#
# 1. Every variable should be defined in the ad hoc VARIABLES section with a
#    relevant subsection
# 2. Every new rule should be defined in the ad hoc RULES section with a
#    relevant subsection depending on the targeted service
# 3. Rules should be sorted alphabetically within their section
# 4. When a rule has multiple dependencies, you should:
#    - duplicate the rule name to add the help string (if required)
#    - write one dependency per line to increase readability and diffs
# 5. .PHONY rule statement should be written after the corresponding rule
# ==============================================================================
# VARIABLES

BOLD := \033[1m
RESET := \033[0m
GREEN := \033[1;32m


# -- Database

DB_HOST            = postgresql
DB_PORT            = 5432

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID          = $(shell id -u)
DOCKER_GID          = $(shell id -g)
DOCKER_USER         = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE             = DOCKER_USER=$(DOCKER_USER) docker compose
COMPOSE_EXEC        = $(COMPOSE) exec
COMPOSE_EXEC_APP    = $(COMPOSE_EXEC) app-dev
COMPOSE_RUN         = $(COMPOSE) run --rm
COMPOSE_RUN_APP     = $(COMPOSE_RUN) app-dev
COMPOSE_RUN_CROWDIN = $(COMPOSE_RUN) crowdin crowdin
WAIT_DB             = @$(COMPOSE_RUN) dockerize -wait tcp://$(DB_HOST):$(DB_PORT) -timeout 60s
WAIT_KC_DB          = $(COMPOSE_RUN) dockerize -wait tcp://kc_postgresql:5432 -timeout 60s

# -- Backend
MANAGE              = $(COMPOSE_RUN_APP) python manage.py
MAIL_YARN           = $(COMPOSE_RUN) -w /app/src/mail node yarn
TSCLIENT_YARN       = $(COMPOSE_RUN) -w /app/src/tsclient node yarn

# -- Frontend
PATH_FRONT          = ./src/frontend
PATH_FRONT_DESK     = $(PATH_FRONT)/apps/desk

# ==============================================================================
# RULES

default: help

data/media:
	@mkdir -p data/media

data/static:
	@mkdir -p data/static

# -- Project

create-env-files: ## Copy the dist env files to env files
create-env-files: \
	env.d/development/common \
	env.d/development/france \
	env.d/development/crowdin \
	env.d/development/postgresql \
	env.d/development/kc_postgresql
.PHONY: create-env-files

bootstrap: ## Prepare Docker images for the project and install frontend dependencies
bootstrap: \
	data/media \
	data/static \
	create-env-files \
	build \
	run \
	migrate \
	back-i18n-compile \
	mails-install \
	mails-build \
	dimail-setup-db \
	install-front-desk
.PHONY: bootstrap

# -- Docker/compose
build: ## build the app-dev container
	@$(COMPOSE) build app-dev
.PHONY: build

down: ## stop and remove containers, networks, images, and volumes
	@$(COMPOSE) down
.PHONY: down

logs: ## display app-dev logs (follow mode)
	@$(COMPOSE) logs -f app-dev
.PHONY: logs

run: ## start the wsgi (production) and development server
	@$(COMPOSE) up --force-recreate -d nginx
	@$(COMPOSE) up --force-recreate -d app-dev
	@$(COMPOSE) up --force-recreate -d celery-dev
	@$(COMPOSE) up --force-recreate -d keycloak
	@$(COMPOSE) up -d dimail
	@echo "Wait for postgresql to be up..."
	@$(WAIT_KC_DB)
	@$(WAIT_DB)
.PHONY: run

status: ## an alias for "docker compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop the development server using Docker
	@$(COMPOSE) stop
.PHONY: stop

# -- Backend

demo: ## flush db then create a demo for load testing purpose
	@$(MAKE) resetdb
	@$(MANAGE) create_demo
.PHONY: demo


# Nota bene: Black should come after isort just in case they don't agree...
lint: ## lint back-end python sources
lint: \
  lint-ruff-format \
  lint-ruff-check \
  lint-pylint
.PHONY: lint

lint-ruff-format: ## format back-end python sources with ruff
	@echo 'lint:ruff-format started…'
	@$(COMPOSE_RUN_APP) ruff format .
.PHONY: lint-ruff-format

lint-ruff-check: ## lint back-end python sources with ruff
	@echo 'lint:ruff-check started…'
	@$(COMPOSE_RUN_APP) ruff check . --fix
.PHONY: lint-ruff-check

lint-pylint: ## lint back-end python sources with pylint only on changed files from main
	@echo 'lint:pylint started…'
	bin/pylint --diff-only=origin/main
.PHONY: lint-pylint

test: ## run project tests
	@$(MAKE) test-back-parallel
.PHONY: test

test-back: ## run back-end tests
	@args="$(filter-out $@,$(MAKECMDGOALS))" && \
	bin/pytest $${args:-${1}}
.PHONY: test-back

test-back-parallel: ## run all back-end tests in parallel
	@args="$(filter-out $@,$(MAKECMDGOALS))" && \
	bin/pytest -n auto $${args:-${1}}
.PHONY: test-back-parallel

test-coverage: ## compute, display and save test coverage
	bin/pytest --cov=. --cov-report json .
.PHONY: test-coverage

makemigrations:  ## run django makemigrations for the people project.
	@echo "$(BOLD)Running makemigrations$(RESET)"
	@$(COMPOSE) up -d postgresql
	@$(WAIT_DB)
	@$(MANAGE) makemigrations $(ARGS)
.PHONY: makemigrations

migrate:  ## run django migrations for the people project.
	@echo "$(BOLD)Running migrations$(RESET)"
	@$(COMPOSE) up -d postgresql
	@$(WAIT_DB)
	@$(MANAGE) migrate $(ARGS)
.PHONY: migrate

showmigrations:  ## run django showmigrations for the people project.
	@echo "$(BOLD)Running showmigrations$(RESET)"
	@$(COMPOSE) up -d postgresql
	@$(WAIT_DB)
	@$(MANAGE) showmigrations $(ARGS)
.PHONY: showmigrations

superuser: ## Create an admin superuser with password "admin"
	@echo "$(BOLD)Creating a Django superuser$(RESET)"
	$(MANAGE) createsuperuser --username admin --password admin

.PHONY: superuser

back-i18n-compile: ## compile the gettext files
	@$(MANAGE) compilemessages --ignore="venv/**/*"
.PHONY: back-i18n-compile

back-i18n-generate: ## create the .pot files used for i18n
	@$(MANAGE) makemessages -a --keep-pot
.PHONY: back-i18n-generate

shell: ## connect to database shell
	@$(MANAGE) shell #_plus
.PHONY: dbshell

# -- Database

dbshell: ## connect to database shell
	docker compose exec app-dev python manage.py dbshell
.PHONY: dbshell

resetdb: FLUSH_ARGS ?=
resetdb: ## flush database and create a superuser "admin"
	@echo "$(BOLD)Flush database$(RESET)"
	@$(MANAGE) flush $(FLUSH_ARGS)
	@${MAKE} superuser
.PHONY: resetdb

env.d/development/common:
	cp -n env.d/development/common.dist env.d/development/common

env.d/development/france:
	cp -n env.d/development/france.dist env.d/development/france

env.d/development/postgresql:
	cp -n env.d/development/postgresql.dist env.d/development/postgresql

env.d/development/kc_postgresql:
	cp -n env.d/development/kc_postgresql.dist env.d/development/kc_postgresql

# -- Internationalization

env.d/development/crowdin:
	cp -n env.d/development/crowdin.dist env.d/development/crowdin

crowdin-download: ## Download translated message from Crowdin
	@$(COMPOSE_RUN_CROWDIN) download -c crowdin/config.yml
.PHONY: crowdin-download

crowdin-download-sources: ## Download sources from Crowdin
	@$(COMPOSE_RUN_CROWDIN) download sources -c crowdin/config.yml
.PHONY: crowdin-download-sources

crowdin-upload: ## Upload source translations to Crowdin
	@$(COMPOSE_RUN_CROWDIN) upload sources -c crowdin/config.yml
.PHONY: crowdin-upload

i18n-compile: ## compile all translations
i18n-compile: \
	back-i18n-compile \
	frontend-i18n-compile
.PHONY: i18n-compile

i18n-generate: ## create the .pot files and extract frontend messages
i18n-generate: \
	back-i18n-generate \
	frontend-i18n-generate
.PHONY: i18n-generate

i18n-download-and-compile: ## download all translated messages and compile them to be used by all applications
i18n-download-and-compile: \
  crowdin-download \
  i18n-compile
.PHONY: i18n-download-and-compile

i18n-generate-and-upload: ## generate source translations for all applications and upload them to Crowdin
i18n-generate-and-upload: \
  i18n-generate \
  crowdin-upload
.PHONY: i18n-generate-and-upload

# -- INTEROPERABILTY
# -- Dimail configuration

recreate-dimail-container:
	@$(COMPOSE) up --force-recreate -d dimail
.PHONY: recreate-dimail-container

dimail-setup-db:
	@echo "$(BOLD)Populating database of local dimail API container$(RESET)"
	@$(MANAGE) setup_dimail_db
.PHONY: dimail-setup-db

# -- Mail generator

mails-build: ## Convert mjml files to html and text
	@$(MAIL_YARN) build
.PHONY: mails-build

mails-build-html-to-plain-text: ## Convert html files to text
	@$(MAIL_YARN) build-html-to-plain-text
.PHONY: mails-build-html-to-plain-text

mails-build-mjml-to-html:	## Convert mjml files to html and text
	@$(MAIL_YARN) build-mjml-to-html
.PHONY: mails-build-mjml-to-html

mails-install: ## install the mail generator
	@$(MAIL_YARN) install
.PHONY: mails-install

# -- TS client generator

tsclient-install: ## Install the Typescript API client generator
	@$(TSCLIENT_YARN) install
.PHONY: tsclient-install

tsclient: tsclient-install ## Generate a Typescript API client
	@$(TSCLIENT_YARN) generate:api:client:local ../frontend/tsclient
.PHONY: tsclient-install

# -- Misc
clean: ## restore repository state as it was freshly cloned
	git clean -idx
.PHONY: clean

help:
	@echo "$(BOLD)People Makefile"
	@echo "Please use 'make $(BOLD)target$(RESET)' where $(BOLD)target$(RESET) is one of:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-30s$(RESET) %s\n", $$1, $$2}'
.PHONY: help

# Front 
install-front-desk: ## Install the frontend dependencies of app Desk  
	cd $(PATH_FRONT_DESK) && yarn && yarn playwright install chromium
.PHONY: install-front-desk

run-front-desk: ## Start app Desk  
	cd $(PATH_FRONT_DESK) && yarn dev
.PHONY: run-front-desk

frontend-i18n-extract: ## Extract the frontend translation inside a json to be used for crowdin
	cd $(PATH_FRONT) && yarn i18n:extract
.PHONY: frontend-i18n-extract

frontend-i18n-generate: ## Generate the frontend json files used for crowdin
frontend-i18n-generate: \
	crowdin-download-sources \
	frontend-i18n-extract
.PHONY: frontend-i18n-generate

frontend-i18n-compile: ## Format the crowin json files used deploy to the apps
	cd $(PATH_FRONT) && yarn i18n:deploy
.PHONY: frontend-i18n-compile

# -- K8S
start-kind: ## Create the kubernetes cluster
	./bin/start-kind.sh
.PHONY: start-kind

install-external-secrets: ## install the kubernetes secrets from Vaultwarden
	./bin/install-external-secrets.sh
.PHONY: build-k8s-cluster

tilt-up: ## start tilt - k8s local development
	tilt up -f ./bin/Tiltfile
.PHONY: tilt-up

start-tilt-keycloak: ## start the kubernetes cluster using kind, without Pro Connect for authentication, use keycloak
	DEV_ENV=dev-keycloak tilt up -f ./bin/Tiltfile
.PHONY: build-k8s-cluster

start-tilt-authentik:
	DEV_ENV=dev-authentik tilt up -f ./bin/Tiltfile
.PHONY: start-tilt-authentik

release:  ## helper for release and deployment
	python scripts/release.py
.PHONY: release

install-secret: ## install the kubernetes secrets from Vaultwarden
	if kubectl -n desk get secrets bitwarden-cli-desk; then \
		echo "Secret already present"; \
	else \
		echo "Please provide the following information:"; \
		read -p "Enter your vaultwarden email login: " LOGIN; \
		read -p "Enter your vaultwarden password: " PASSWORD; \
		read -p "Enter your vaultwarden server url: " URL; \
		echo "\nCreate vaultwarden secret"; \
		echo "apiVersion: v1" > /tmp/secret.yaml; \
		echo "kind: Secret" >> /tmp/secret.yaml; \
		echo "metadata:" >> /tmp/secret.yaml; \
		echo "  name: bitwarden-cli-desk" >> /tmp/secret.yaml; \
		echo "  namespace: desk" >> /tmp/secret.yaml; \
		echo "type: Opaque" >> /tmp/secret.yaml; \
		echo "stringData:" >> /tmp/secret.yaml; \
		echo "  BW_HOST: $$URL" >> /tmp/secret.yaml; \
		echo "  BW_PASSWORD: $$PASSWORD" >> /tmp/secret.yaml; \
		echo "  BW_USERNAME: $$LOGIN" >> /tmp/secret.yaml; \
		kubectl -n desk apply -f /tmp/secret.yaml;\
		rm -f /tmp/secret.yaml; \
	fi; \
	if kubectl get ns external-secrets; then \
		echo "External secret already deployed"; \
	else \
		helm repo add external-secrets https://charts.external-secrets.io; \
		helm upgrade --install external-secrets \
      external-secrets/external-secrets \
       -n external-secrets \
       --create-namespace \
       --set installCRDs=true; \
	fi
.PHONY: build-k8s-cluster

fetch-domain-status:
	@$(MANAGE) fetch_domain_status
.PHONY: fetch-domain-status
