# People as an Identity Provider

The people project can be configured to act as an Identity Provider for an OIDC federation.

The model containing the "identity" in `people` is the `Mailbox` model.

The connection workflow looks like:

 - The user tries to reach a service provider.
 - The service provider redirects the user to OIDC federation (in dev we use Keycloak).
 - The user asks (or is redirected) to the Identity Provider (people).
 - The user enter their email and password.
 - If successful, the user is redirected to the OIDC federation with a token.
 - The federation make the same Authorization Flow as usual to authenticate on the Service Provider.


## Technical aspects

### The `Mailbox` model

The `Mailbox` model can behave like a usual Django user:

 - It has a `password` field (and `last_login`)
 - It is considered as `authenticated`.
 - To be `active` it must have an `enabled` status.
 - To be able to log in, it must also have a `MailboxDomain` with an `enabled` status and an associated `Organization`.

### The `MailboxModelBackend` authentication backend

This authentication backend only allow authentication with `email` and `password` with a `Mailbox` user.
This backend is combined with the `one_time_email_authenticated_session` middleware to restrict
the session to the OIDC login process.
A user connecting with this backend will only be able to access the `/o/authorize/` URL.

### The OIDC validators

There are two validators available:

 - `BaseValidator`: This validator retrieves simple claims
 - `ProConnectValidator`: This validator is a custom validator to allow ProConnect specific requirements.


## Configuration

The keycloak configuration is not described here, but you may find information in the code base.

### Django settings

The following settings are required to enable the OIDC Identity Provider feature:

 - OAUTH2_PROVIDER_OIDC_ENABLED: True
 - OAUTH2_PROVIDER_OIDC_RSA_PRIVATE_KEY: ...

Optional:

 - OAUTH2_PROVIDER_VALIDATOR_CLASS: "mailbox_oauth2.validators.ProConnectValidator"

If the `OAUTH2_PROVIDER_VALIDATOR_CLASS` is set to the `ProConnectValidator`, the claims will be
automatically defined to match the ProConnect requirements.

### Django OIDC application

To enable an OIDC client to use people, you must declare it.

```python
from oauth2_provider.models import Application

application = Application(
    client_id="people-idp",
    client_secret="local-tests-only",
    client_type=Application.CLIENT_CONFIDENTIAL,
    authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
    name="People Identity Provider",
    algorithm=Application.RS256_ALGORITHM,
    redirect_uris="http://localhost:8083/realms/people/broker/oidc-people-local/endpoint",
    skip_authorization=True,
)
application.clean()
application.save()
```

## Security concerns

### Failed login cooldown

To prevent brute force attacks, 5 failed login will trigger a cooldown of 5 minutes before being able to log in again.

### Password strength

There is currently no constraint on the password strength as it can only be defined by Django administrators,
and later we will generate it.
If at some point the user is allowed to set their password, we will need to enforce a password strength policy.


## What is missing (next steps)

- `Mailbox` password can only be set through Django Admin panel (or shell), the next step will be to generate 
  a secure password and send it or display it to the end user.
- `MailboxDomain` organization can only be set through Django Admin panel (or shell), we need to provide a
  way to auto-select it or allow an administrator to do so.
