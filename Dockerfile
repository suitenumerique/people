# Django People

# ---- base image to inherit from ----
FROM python:3.12.9-alpine3.21 AS base

# Upgrade pip to its latest release to speed up dependencies installation
RUN python -m pip install --upgrade pip setuptools

# Upgrade system packages to install security updates
RUN apk update && \
  apk upgrade

### ---- Front-end dependencies image ----
FROM node:20 AS frontend-deps

WORKDIR /deps

COPY ./src/frontend/package.json ./package.json
COPY ./src/frontend/yarn.lock ./yarn.lock
COPY ./src/frontend/apps/desk/package.json ./apps/desk/package.json
COPY ./src/frontend/packages/i18n/package.json ./packages/i18n/package.json
COPY ./src/frontend/packages/eslint-config-people/package.json ./packages/eslint-config-people/package.json

RUN yarn --frozen-lockfile

### ---- Front-end builder dev image ----
FROM node:20 AS frontend-builder-dev

WORKDIR /builder

COPY --from=frontend-deps /deps/node_modules ./node_modules
COPY ./src/frontend .

WORKDIR ./apps/desk

### ---- Front-end builder image ----
FROM frontend-builder-dev AS frontend-builder

RUN yarn build

# ---- Front-end image ----
FROM nginxinc/nginx-unprivileged:1.26-alpine AS frontend-production

# Un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

COPY --from=frontend-builder \
    /builder/apps/desk/out \
    /usr/share/nginx/html

COPY ./src/frontend/apps/desk/conf/default.conf /etc/nginx/conf.d

# Copy entrypoint
COPY ./docker/files/usr/local/bin/entrypoint /usr/local/bin/entrypoint

ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

CMD ["nginx", "-g", "daemon off;"]


# ---- Back-end builder image ----
FROM base AS back-builder

WORKDIR /builder

# Copy required python dependencies
COPY ./src/backend /builder

RUN mkdir /install && \
  pip install --prefix=/install .


# ---- mails ----
FROM node:20 AS mail-builder

COPY ./src/mail /mail/app

WORKDIR /mail/app

RUN yarn install --frozen-lockfile && \
    yarn build


# ---- static link collector ----
FROM base AS link-collector
ARG PEOPLE_STATIC_ROOT=/data/static

# Install libpangocairo & rdfind
RUN apk add \
  pango \
  rdfind

# Copy installed python dependencies
COPY --from=back-builder /install /usr/local

# Copy people application (see .dockerignore)
COPY ./src/backend /app/

WORKDIR /app

# collectstatic
RUN DJANGO_CONFIGURATION=Build DJANGO_JWT_PRIVATE_SIGNING_KEY=Dummy \
    python manage.py collectstatic --noinput

# Replace duplicated file by a symlink to decrease the overall size of the
# final image
RUN rdfind -makesymlinks true -followsymlinks true -makeresultsfile false ${PEOPLE_STATIC_ROOT}

# ---- Core application image ----
FROM base AS core

ENV PYTHONUNBUFFERED=1

# Install required system libs
RUN apk add \
  gettext \
  cairo \
  libffi-dev \
  gdk-pixbuf \
  pango \
  shared-mime-info

# Copy entrypoint
COPY ./docker/files/usr/local/bin/entrypoint /usr/local/bin/entrypoint

# Give the "root" group the same permissions as the "root" user on /etc/passwd
# to allow a user belonging to the root group to add new users; typically the
# docker user (see entrypoint).
RUN chmod g=u /etc/passwd

# Copy installed python dependencies
COPY --from=back-builder /install /usr/local

# Copy people application (see .dockerignore)
COPY ./src/backend /app/

WORKDIR /app

# We wrap commands run in this container by the following entrypoint that
# creates a user on-the-fly with the container user ID (see USER) and root group
# ID.
ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

# ---- Development image ----
FROM core AS backend-development

# Switch back to the root user to install development dependencies
USER root:root

# Install psql
RUN apk add postgresql-client

# Uninstall people and re-install it in editable mode along with development
# dependencies
RUN pip uninstall -y people
RUN pip install -e .[dev]

# Restore the un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# Target database host (e.g. database engine following docker compose services
# name) & port
ENV DB_HOST=postgresql \
    DB_PORT=5432

# Run django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ---- Production image ----
FROM core AS backend-production

ARG PEOPLE_STATIC_ROOT=/data/static

# Gunicorn
RUN mkdir -p /usr/local/etc/gunicorn
COPY docker/files/usr/local/etc/gunicorn/people.py /usr/local/etc/gunicorn/people.py

# Un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# Copy statics
COPY --from=link-collector ${PEOPLE_STATIC_ROOT} ${PEOPLE_STATIC_ROOT}

# Copy people mails
COPY --from=mail-builder /mail/backend/core/templates/mail /app/core/templates/mail

# The default command runs gunicorn WSGI server in people's main module
CMD ["gunicorn", "-c", "/usr/local/etc/gunicorn/people.py", "people.wsgi:application"]
