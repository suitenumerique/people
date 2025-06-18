# People

People is an application to handle users and teams, and distribute permissions accross [La Suite](https://lasuite.numerique.gouv.fr/).

It is built on top of [Django Rest
Framework](https://www.django-rest-framework.org/).

All interoperabilities will be described in `docs/interoperability`.

## Getting started

### Prerequisite

Make sure you have a recent version of Docker and [Docker
Compose](https://docs.docker.com/compose/install) installed on your laptop:

```bash
$ docker -v
  Docker version 20.10.2, build 2291f61

$ docker compose -v
  docker compose version 1.27.4, build 40524192
```

> ⚠️ You may need to run the following commands with `sudo` but this can be
> avoided by assigning your user to the `docker` group.

### Bootstrap project

The easiest way to start working on the project is to use GNU Make:

```bash
$ make bootstrap
```

This command builds the `app-dev` container, installs dependencies, performs
database migrations and compile translations. It's a good idea to use this
command each time you are pulling code from the project repository to avoid
dependency-related or migration-related issues.

Your Docker services should now be up and running! 🎉

Note that if you need to run them afterward, you can use the eponym Make rule:

```bash
$ make run
```

or if you want to run them in development mode (with live reloading):

```bash
$ make run-dev
```

You can check all available Make rules using:

```bash
$ make help
```

### Django admin

You can access the Django admin site at
[http://localhost:8071/admin](http://localhost:8071/admin).

You first need to create a superuser account:

```bash
$ make superuser
```

You can then login with sub `admin` and password `admin`.

### Adding demo content

You can create a basic demo site by running:

```bash
$ make demo
```

### Setting dimail database 

To ease local development when working on interoperability between people and dimail, we embark dimail-api in a container running in "fake" mode. 

To populate dimail local database with users/domains/permissions needed for basic development:
- log in with "people" user
- run `make dimail-setup-db`


### Run frontend

Run the front with:

```bash
$ make run-front-desk
```

Then access [http://localhost:3000](http://localhost:3000) with :
user: people
password: people

## Contributing

This project is intended to be community-driven, so please, do not hesitate to
get in touch if you have any question related to our implementation or design
decisions.

## License

This work is released under the MIT License (see [LICENSE](./LICENSE)).
