# dimail 

## What is dimail ? 

The mailing solution provided in La Suite is [La Messagerie](https://webmail.numerique.gouv.fr/), using [Open-XChange](https://www.open-xchange.com/) (OX). OX not having a provisioning API, 'dimail-api' or 'dimail' was created to allow mail-provisioning through People.

Dimail-api and its documentation can be found [here](https://api.osprod.dimail1.numerique.gouv.fr/docs#/).

## Features

### Domains

#### Domain creation 

Upon creating a domain on People, the same domain is created on Messagerie and will undergo a series of checks. The DNS configuration provided by Messagerie can be found in domain administration menu.

Domains configuration is checked every hour. When Messagerie's checks return successful, the domain status in People is set to "enabled".  

> [!NOTE]
> On Messagerie, domains belong to a group called "context". "Contexts" are shared spaces between domains, allowing users to discover colleagues not only on their domain but on their entire context.


> Contexts are only implemented in Messagerie and are not currently in use in People. Domains created via People are in their own context. Please contact our support team if you want several domains to be moved to a single context.

### Mailboxes 

Mailboxes can be created by a domain owners or administrators in People's domain tab.

On enabled domains, mailboxes are created at the same time on dimail (and a confirmation email is sent to the secondary email).
On pending/failed domains, mailboxes are only created locally with "pending" status and are sent to dimail upon domain's (re)activation.
On disabled domains, mailboxes creation is not allowed.

## Permissions

Users can have 3 levels of permissions on a domain

|                   | on domain                                                                                                                 | on mailboxes                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Owners            | - promote administrators owners<br>- all of viewers and administrators' permissions                                       |                                                                   |
| Administrators    | - create mailboxes<br>- invite users to manage domain<br>- promote viewers to administrators<br>- all viewers permissions | - deactivate mailbox<br>- send login link<br>- update information |
| Viewers           | - see the domain's information<br>- list its mailboxes<br>                                                                | - update information on own mailbox<br>- send login link          |
| No role           | Cannot see domain. Requests return a 404_NOT_FOUND                                                                        | - none                                                            |
| Not authenticated | Cannot see domain. Requests return a 401_NOT_AUTHENTICATED <br>                                                           | - none                                                            |

## For devs

## Use of dimail container

To ease local development, dimail provides a container that we embark in our docker-compose. In "FAKE" mode, it simulates all responses from Open Exchange.

Bootstraping with command `make bootstrap` creates a container and initializes its database.

Additional commands : 
- Reset and populate the database with all the content of your People database with `dimail-setup-db`

## Architecture

### Domains

Upon creating a domain on People, the same domain is created on dimail and will undergo a series of checks. When all checks have passed, the domain is considered enabled. 

Domains in OX have a field called "context". "Contexts" are shared spaces between domains, allowing users to discover users not only on their domain but on their entire context.
> [!NOTE]   
> Contexts are only implemented in La Messagerie and are not currently in use in People. Domains created via People are in their own context.

People users can have 3 levels of permissions on a domain:
- Viewers can
    - see the domain's information
    - list its mailboxes and managers
- Administrators can
    - create mailboxes
    - invite collaborators to manage domain
    - change role of a viewer to administrators
    - all of viewers permissions
- Owners can
    - promote administrators owners and demote owners
    - all of viewers and administrators' permissions
> [!NOTE]   
> Contexts are only implemented in La Messagerie and are not currently in use in People. Domains created via People are in their own context.


### Mailboxes 

Mailboxes can be created by a domain owners or administrators in People's domain tab.

On enabled domains, mailboxes are created at the same time on dimail (and a confirmation email is sent to the secondary email).
On pending/failed domains, mailboxes are only created locally with "pending" status and are sent to dimail upon domain's (re)activation.
On disabled domains, mailboxes creation is not allowed.
