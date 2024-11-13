# E2E tests

## Run E2E tests

``` bash
# you need the dockers to be up and running
make bootstrap

# you will need to have few accounts in the database
make demo FLUSH_ARGS='--no-input'

# run the tests
cd src/frontend/apps/e2e
yarn test:ui --workers=1
```

A new browser window will open and you will be able to run the tests.

## Available accounts

The `make demo` command creates the following accounts:
 - `jean.team-<role>@example.com` where `<role>` is one of `administrator`, `member`, `owner`:
    this account only belong to a team with the specified role.
 - `jean.mail-<role>@example.com` where `<role>` is one of `administrator`, `member`, `owner`:
    this account only have a mailbox with the specified role access.
 - `jean.team-<team_role>-mail-<domain_role>@example.com` with a combination of roles as for the
    previous accounts.

For each account, the password is `password-e2e-<username>`, for instance `password-e2e-jean.team-member`.

In the E2E tests you can use these accounts to benefit from there accesses, 
using the `keyCloakSignIn(page, browserName, <account_name>)`. The account name is the 
username without the prefix `jean.`.

``` typescript jsx
await keyCloakSignIn(page, browserName, 'mail-owner');
```

The `keyCloakSignIn` function will sign in the user on Keycloak using the proper username and password.

.. note::
    This only works because the OIDC setting is set to fallback on user email.

## Add a new account

In case you need to add a new account for specific tests you need:
- to create a new user with the same format in the backend database: 
  update `[create_demo.py](../src/backend/demo/management/commands/create_demo.py)`
- to create a new account in Keycloak: update [realm.json](../docker/auth/realm.json)
- if the keycloak was running locally, you need to destroy its database and 
  restart the database and the keycloak containers.
