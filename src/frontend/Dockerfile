FROM node:22-alpine AS frontend-deps

# Upgrade system packages to install security updates
RUN apk update && \
  apk upgrade && \
  rm -rf /var/cache/apk/*

WORKDIR /home/frontend/

COPY ./src/frontend/package.json ./package.json
COPY ./src/frontend/yarn.lock ./yarn.lock
COPY ./src/frontend/apps/desk/package.json ./apps/desk/package.json
COPY ./src/frontend/packages/i18n/package.json ./packages/i18n/package.json
COPY ./src/frontend/packages/eslint-config-people/package.json ./packages/eslint-config-people/package.json

RUN yarn install --frozen-lockfile

COPY .dockerignore ./.dockerignore
COPY ./src/frontend/.prettierrc.js ./.prettierrc.js
COPY ./src/frontend/packages/eslint-config-people ./packages/eslint-config-people
COPY ./src/frontend/apps/desk ./apps/desk

### ---- Front-end builder image ----
FROM frontend-deps AS frontend-base

WORKDIR /home/frontend/apps/desk

### ---- Front-end builder dev image ----
FROM frontend-deps AS frontend-dev

WORKDIR /home/frontend/apps/desk

EXPOSE 3000

CMD [ "yarn", "dev"]


FROM frontend-base AS frontend-builder

WORKDIR /home/frontend/apps/desk

ARG API_ORIGIN
ENV NEXT_PUBLIC_API_ORIGIN=${API_ORIGIN}

RUN yarn build

# ---- Front-end image ----
FROM nginxinc/nginx-unprivileged:alpine3.21 AS frontend-production

# Un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

COPY --from=frontend-builder \
    /home/frontend/apps/desk/out \
    /usr/share/nginx/html

COPY ./src/frontend/apps/desk/conf/default.conf /etc/nginx/conf.d
COPY ./docker/files/usr/local/bin/entrypoint /usr/local/bin/entrypoint

ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

CMD ["nginx", "-g", "daemon off;"]
