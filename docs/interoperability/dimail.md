# dimail 

## What is dimail ? 

The mailing solution provided in La Suite is [Open-XChange](https://www.open-xchange.com/) (OX). 
OX not having a provisioning API, 'dimail-api' or 'dimail' was created to allow mail-provisioning through People.

API and its documentation can be found [here](https://api.dev.ox.numerique.gouv.fr/docs#/).

## Architectural links of dimail

As dimail's primary goal is to act as an interface between People and OX, its architecture is similar to that of People. A series of requests are sent from People to dimail upon creating domains, users and accesses.

### Domains

Upon creating a domain on People, the same domain is created on dimail and will undergo a series of checks. When all checks have passed, the domain is considered valid and mailboxes can be created on it. 

Domains in OX have a field called "context". Context is a shared space between domains, allowing users to discover users not only on their domain but on their entire context.

### Users

The ones issuing requests. Dimail users will reflect domains owners and administrators on People, for logging purposes and to allow direct use of dimail, if desired. User reconciliation is made on user uuid provided by ProConnect.

### Accesses

As for People, an access - a permissions (or "allows" in dimail) - grants an user permission to create objects on a domain.

Permissions requests are sent automatically upon : 
- dimail database initialisation: 
    + permission for dimail user People to create users and domains
- domain creation : 
    + permission for dimail user People to manage domain
    + permission for new owner on new domain
- user creation:
    + permission for People to manage user
- access creation, if owner or admin:
    + permission for this user to manage domain