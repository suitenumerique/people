# dimail 

## What is dimail ? 

The mailing solution provided in LaSuite is [Messagerie](https://webmail.numerique.gouv.fr/), using [Open-XChange](https://www.open-xchange.com/) (OX). OX currently does not provide a provisioning API, hence 'dimail', meant as an interface between Messagerie and outside parties such as People.

Dimail-api and its documentation can be found [here](https://api.osprod.dimail1.numerique.gouv.fr/docs#/).

## Features

### Domain creation

Upon creating a domain on People, the same domain is created on Messagerie and will undergo a series of checks. The DNS configuration provided by Messagerie can be found in domain administration menu.

Domains configuration is checked every hour. When Messagerie's checks return successful, the domain status in People is set to "enabled".  

> [!NOTE]
> On Messagerie, domains belong to a group called "context". "Contexts" are shared spaces between domains, allowing users to discover colleagues not only on their domain but on their entire context.


> Contexts are only implemented in Messagerie and are not currently in use in People. Domains created via People are in their own context. Please contact our support team if you want several domains to be moved to a single context.

### Mailbox management

Mailboxes can be created by a domain owners or administrators in People's domain tab and are created on dimail too.
A confirmation email is sent to secondary email if provided, containing a one-time login link. 

Mailboxes can be deactivated

## Permissions

Users can have 3 levels of permissions on a domain

|                   | on domain                                                                                                                 | on mailboxes                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Owners            | - promote administrators owners<br>- all of viewers and administrators' permissions                                       |                                                                   |
| Administrators    | - create mailboxes<br>- invite users to manage domain<br>- promote viewers to administrators<br>- all viewers permissions | - deactivate mailbox<br>- send login link<br>- update information |
| Viewers           | - see the domain's information<br>- list its mailboxes<br>                                                                | - update information on own mailbox<br>- send login link          |
| No role           | Cannot see domain. Requests return a 404_NOT_FOUND                                                                        | - none                                                            |
| Not authenticated | Cannot see domain. Requests return a 401_NOT_AUTHENTICATED <br>                                                           | - none                                                            |                                                   |

## For devs

## Use of dimail container

To ease local development, dimail provides a container that we embark on our docker stack. In "FAKE" mode, dimail container simulates all responses from Open Exchange, providing an environment close to production.

Bootstraping with command `make dimail-setup-db` creates the container and populates its database from People's database.
