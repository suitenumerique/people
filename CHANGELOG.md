# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 🧑‍💻(admin) export domain contact info #1061

### Fixed

- 🐛(dimail) fix no import for functional mailboxes

## [1.24.0] - 2026-03-24

### Fixed

- ✨(mailboxes) enforce lowercase on mailboxes
- 🐛(i18n) fix missing translations for status tag labels
- 🚚(route) prioritize mail domains as default landing page

### Changed

- 💄(config) update ui configuration domain modale
- 🍱(static) update logo in invitation email template #1085
- ✨(uiV2) use Lasuite UI kit, new layout

## [1.23.1] - 2026-02-16

- ✨(invitations) refresh expired invitations

## [1.23.0] - 2026-02-12

### Added

- ✨(demo) add aliases to demo #1050
- ✨(front) add icon to button to configure a domain
- ✨(datagrid) add sort to mailboxes list + mail domain list
- ✨(invitations) allow delete invitations mails domains access by an admin
- ✨(front) delete invitations mails domains access
- ✨(front) add show invitations mails domains access #1040
- ✨(invitations) can delete domain invitations

### Fixed

- 🐛(domains) fix attemps to send invitations to existing users #953

### Changed

- 🚸(email) we should ignore case when looking for existing emails #1056
- 🏗️(core) migrate from pip to uv
- ✨(front) add show invitations mails domains access #1040

## [1.22.2] - 2026-01-26

### Fixed

- 🐛(aliases) authorize special domain devnull in alias destinations #1029 

## [1.22.1] - 2026-01-21

- 🔒️(organization) the first user is not admin #776
- 🐛(admin) fix broken alias import #1021

## [1.22.0] - 2026-01-19

### Added
- ✨(front) create, manage & delete aliases
- ✨(domains) alias sorting and admin
- ✨(aliases) delete all aliases in one call #1002

### Fixed
- 🔒️(security) upgrade python version to fix vulnerability #1010
- 🐛(dimail) ignore oxadmin when importing mailboxes from dimail #986
- ✨(aliases) fix deleting single aliases #1002

### Changed
- 🐛(dimail) allow mailboxes and aliases to have the same local part #986

### Removed
- 🔥(plugins) remove CommuneCreation plugin

## [1.21.0] - 2025-12-05

- ✨(aliases) import existing aliases from dimail
- 🛂(permissions) return 404 to users with no access to domain #985 
- ✨(aliases) can create, list and delete aliases #974

## [1.20.0] - 2025-10-22

- ✨(models) impose uniqueness on display name, to match ox's constraint
- 🐛(dimail) catch duplicate displayname error
- ✨(mailbox) synchronize password of newly created mailbox with Dimail's

## [1.19.1] - 2025-09-19

- 🐛(fix) add enabled update your mailbox

## [1.19.0] - 2025-09-03

- ✨(front) add modal update mailboxes #954

### Added

- ✨(api) update mailboxes #934
- ✨(api) give update rights to domain viewer on own mailbox #934

### Fixed

- 🐛(dimail) grab duplicate displayname error #961

### Changed

- 💥(sentry) remove `DJANGO_` before Sentry DSN env variable #957

## [1.18.2] - 2025-07-03

### Fixed

- 🐛(front) fix missing pagination mail domains #950

## [1.18.1] - 2025-07-02

### Fixed

- 🐛(front) fix missing pagination on mail domains #946

## [1.18.0] - 2025-06-30

### Added

- 🐛(front) fix missing pagination mail domains
- 🐛(front) fix button add mail domain
- ✨(teams) add matrix webhook for teams #904
- ✨(resource-server) add SCIM /Me endpoint #895
- 🔧(git) set LF line endings for all text files #928

### Changed

- 🧑‍💻(docker) split frontend to another file #924

### Fixed 

- 🐛(webhook) handle user on different home server than room server

## [1.17.0] - 2025-06-11

### Added

- ✨(frontend) add crisp script #914
- ⚡️(fix) add error when mailbox create failed
- ✨(mailbox) allow to reset password on mailboxes #834

## [1.16.0] - 2025-05-05

### Added

- 🔧(sentry) add Celery beat task integration #892

### Changed

- ✨(uiv2) change mail domains
- 🛂(dimail) simplify interop with dimail
- ✨(mailbox) remove secondary email as required field

### Fixed

- 🔒️(drf) disable browsable HTML API renderer #897

## [1.15.0] - 2025-04-04

### Added

- 🧱(helm) add la-suite ingress path
- ➕(backend) add django-lasuite dependency #858
- ✨(plugins) add endpoint to list siret of active organizations #771
- ✨(core) create AccountServiceAuthentication backend #771
- ✨(core) create AccountService model #771
- 🧱(helm) disable createsuperuser job by setting #863
- 🔒️(passwords) add validators for production #850
- ✨(domains) allow to re-run check on domain if status is failed
- ✨(organization) add `is_active` field
- ✨(domains) notify support when domain status changes #668
- ✨(domains) define domain check interval as a settings
- ✨(oidc) add simple introspection backend #832
- 🧑‍💻(tasks) run management commands #814

### Changed

- ♻️(plugins) rewrite plugin system as django app #844
- 🔒️(users) restrict listable users to same organization #846 

### Fixed

- 🐛(dimail) enhance sentry log
- 🐛(oauth2) force JWT signed for /userinfo #804
- 🐛(front) disable retries in useQuery and useInfiniteQuery #818

## [1.14.1] - 2025-03-17

## [1.14.0] - 2025-03-17

### Added

- ✨(domains) enhance required action modal content
- ✨(domains) add periodic tasks to fetch domain status
- 🧑‍💻(docker) add celery beat to manage periodic tasks
- ✨(organization) add metadata field #790
- ⬆️(nginx) bump nginx-unprivileged to 1.27 #797
- ✨(teams) allow broadly available teams #796
- ✨(teams) update and enhance team invitation email
- ✨(api) define dimail timeout as a setting
- ✨(frontend) feature modal add new access role to domain 
- ✨(api) allow invitations for domain management #708

### Fixed

- 🐛(oauth2) force JWT signed for /userinfo #804
- 🐛(oauth2) add ProConnect scopes #802
- 🐛(domains) use a dedicated mail to invite user to manage domain
- 🐛(mailbox) fix mailbox creation email language

## [1.13.1] - 2025-03-04

### Fixed

- 🐛(mailbox) fix migration to fill dn_email field

## [1.13.0] - 2025-03-04

### Added

- ✨(oidc) people as an identity provider #638

### Fixed

- 💄(domains) improve user experience and avoid repeat fix_domain operations
- 👽️(dimail) increase timeout value for check domain API call
- 🧱(helm) add resource-server ingress path #743
- 🌐(backend) synchronize translations with crowdin again

## [1.12.1] - 2025-02-20

### Fixed

- 👽️(dimail) increase timeout value for API calls

## [1.12.0] - 2025-02-18

### Added

- ✨(domains) allow user to re-run all fetch domain data from dimail
- ✨(domains) display DNS config expected for domain with required actions
- ✨(domains) check status after creation
- ✨(domains) display required actions to do on domain
- ✨(plugin) add CommuneCreation plugin with domain provisioning #658
- ✨(frontend) display action required status on domain
- ✨(domains) store last health check details on MailDomain
- ✨(domains) add support email field on domain

## [1.11.0] - 2025-02-07

### Added

- ✨(api) add count mailboxes to MailDomain serializer
- ✨(dimail) manage 'action required' status for MailDomain
- ✨(domains) add action required status on MailDomain
- ✨(dimail) send pending mailboxes upon domain activation

### Fixed

- ✨(auth) fix empty names from ProConnect #687
- 🚑️(teams) do not display add button when disallowed #676
- 🚑️(plugins) fix name from SIRET specific case #674
- 🐛(api) restrict mailbox sync to enabled domains

## [1.10.1] - 2025-01-27

### Added

- ✨(dimail) management command to fetch domain status

### Changed

- ✨(scripts) adapts release script after moving the deployment part

### Fixed

- 🐛(dimail) fix imported mailboxes should be enabled instead of pending #659 
- ⚡️(api) add missing cache for stats endpoint

## [1.10.0] - 2025-01-21

### Added

- ✨(api) create stats endpoint
- ✨(teams) add Team dependencies #560
- ✨(organization) add admin action for plugin #640
- ✨(anct) fetch and display organization names of communes #583
- ✨(frontend) display email if no username #562
- 🧑‍💻(oidc) add ability to pull registration ID (e.g. SIRET) from OIDC #577

### Fixed

- 🐛(frontend) improve e2e tests avoiding race condition from mocks #641
- 🐛(backend) fix flaky test with search contact #605
- 🐛(backend) fix flaky test with team access #646
- 🧑‍💻(dimail) remove 'NoneType: None' log in debug mode
- 🐛(frontend) fix flaky e2e test #636
- 🐛(frontend) fix disable mailbox button display #631
- 🐛(backend) fix dimail call despite mailbox creation failure on our side
- 🧑‍💻(user) fix the User.language infinite migration #611

## [1.9.1] - 2024-12-18

## [1.9.0] - 2024-12-17

### Fixed

- 🐛(backend) fix manage roles on domain admin view

### Added

- ✨(backend) add admin action to check domain health
- ✨(dimail) check domain health
- ✨(frontend) disable mailbox and allow to create pending mailbox
- ✨(organizations) add siret to name conversion #584
- 💄(frontend) redirect home according to abilities #588
- ✨(maildomain_access) add API endpoint to search users #508

## [1.8.0] - 2024-12-12

### Added

- ✨(contacts) add "abilities" to API endpoint data #585
- ✨(contacts) allow filter list API with email
- ✨(contacts) return profile contact from same organization
- ✨(dimail) automate allows requests to dimail
- ✨(contacts) add notes & force full_name #565

### Changed

- ♻️(contacts) move user profile to contact #572
- ♻️(contacts) split api test module in actions #573

### Fixed

- 🐛(backend) fix manage roles on domain admin view
- 🐛(mailbox) fix activate mailbox feature
- 🔧(helm) fix the configuration environment #579

## [1.7.1] - 2024-11-28

## [1.7.0] - 2024-11-28

### Added

- ✨(mailbox) allow to activate mailbox
- ✨(mailbox) allow to disable mailbox
- ✨(backend) add ServiceProvider #522
- 💄(admin) allow header color customization #552 
- ✨(organization) add API endpoints #551

### Fixed

-  🐛(admin) add organization on user #555

## [1.6.1] - 2024-11-22

### Fixed

- 🩹(mailbox) fix status of current mailboxes
- 🚑️(backend) fix claim contains non-user field #548

## [1.6.0] - 2024-11-20

### Removed

- 🔥(teams) remove search by trigram for team access and contact

### Added

- ✨(domains) allow creation of "pending" mailboxes
- ✨(teams) allow team management for team admins/owners #509

### Fixed

-  🔊(backend) update logger config to info #542

## [1.5.0] - 2024-11-14

### Removed

- ⬆️(dependencies) remove unneeded dependencies
- 🔥(teams) remove pagination of teams listing
- 🔥(teams) remove search users by trigram
- 🗃️(teams) remove `slug` field

### Added

- ✨(dimail) send domain creation requests to dimail #454
- ✨(dimail) synchronize mailboxes from dimail to our db #453
- ✨(ci) add security scan #429
- ✨(teams) register contacts on admin views

### Fixed

- 🐛(mail) fix display button on outlook
- 💚(ci) improve E2E tests #492
- 🔧(sentry) restore default integrations
- 🔇(backend) remove Sentry duplicated warning/errors
- 👷(ci) add sharding e2e tests  #467
- 🐛(dimail) fix unexpected status_code for proper debug #454

## [1.4.1] - 2024-10-23

### Fixed

- 🚑️(frontend) fix MailDomainsLayout

## [1.4.0] - 2024-10-23

### Added

- ✨(frontend) add tabs inside #466

### Fixed

- ✏️(mail) fix typo into mailbox creation email
- 🐛(sentry) fix duplicated sentry errors #479
- 🐛(script) improve and fix release script

## [1.3.1] - 2024-10-18

## [1.3.0] - 2024-10-18

### Added

- ✨(api) add RELEASE version on config endpoint #459
- ✨(backend) manage roles on domain admin view
- ✨(frontend) show version number in footer #369
- 👔(backend) add Organization model

### Changed

- 🛂(backend) match email if no existing user matches the sub

### Fixed

- 💄(mail) improve mailbox creation email #462
- 🐛(frontend) fix update accesses form #448
- 🛂(backend) do not duplicate user when disabled

## [1.2.1] - 2024-10-03

### Fixed

- 🔧(mail) use new scaleway email gateway #435 


## [1.2.0] - 2024-09-30


### Added

- ✨(ci) add helmfile linter and fix argocd sync #424 
- ✨(domains) add endpoint to list and retrieve domain accesses #404
- 🍱(dev) embark dimail-api as container #366
- ✨(dimail) allow la regie to request a token for another user #416
- ✨(frontend) show username on AccountDropDown #412
- 🥅(frontend) improve add & update group forms error handling #387
- ✨(frontend) allow group members filtering #363
- ✨(mailbox) send new mailbox confirmation email #397
- ✨(domains) domain accesses update API #423
- ✨(backend) domain accesses create API #428
- 🥅(frontend) catch new errors on mailbox creation #392
- ✨(api) domain accesses delete API #433
- ✨(frontend) add mail domain access management #413

### Fixed

- ♿️(frontend) fix left nav panel #396
- 🔧(backend) fix configuration to avoid different ssl warning #432 

### Changed

- ♻️(serializers) move business logic to serializers #414 

## [1.1.0] - 2024-09-10

### Added

- 📈(monitoring) configure sentry monitoring #378
- 🥅(frontend) improve api error handling #355

### Changed

- 🗃️(models) move dimail 'secret' to settings #372 

### Fixed

- 🐛(dimail) improve handling of dimail errors on failed mailbox creation #377
- 💬(frontend) fix group member removal text #382
- 💬(frontend) fix add mail domain text #382
- 🐛(frontend) fix keyboard navigation #379
- 🐛(frontend) fix add mail domain form submission #355

## [1.0.2] - 2024-08-30

### Added

- 🔧Runtime config for the frontend (#345)
- 🔧(helm) configure resource server in staging

### Fixed 

- 👽️(mailboxes) fix mailbox creation after dimail api improvement (#360)

## [1.0.1] - 2024-08-19

### Fixed

- ✨(frontend) user can add mail domains

## [1.0.0] - 2024-08-09

### Added

- ✨(domains) create and manage domains on admin + API
- ✨(domains) mailbox creation + link to email provisioning API

[unreleased]: https://github.com/suitenumerique/people/compare/v1.24.0...main
[1.24.0]: https://github.com/suitenumerique/people/releases/v1.24.0
[1.23.1]: https://github.com/suitenumerique/people/releases/v1.23.1
[1.23.0]: https://github.com/suitenumerique/people/releases/v1.23.0
[1.22.2]: https://github.com/suitenumerique/people/releases/v1.22.2
[1.22.1]: https://github.com/suitenumerique/people/releases/v1.22.1
[1.22.0]: https://github.com/suitenumerique/people/releases/v1.22.0
[1.21.0]: https://github.com/suitenumerique/people/releases/v1.21.0
[1.20.0]: https://github.com/suitenumerique/people/releases/v1.20.0
[1.19.1]: https://github.com/suitenumerique/people/releases/v1.19.1
[1.19.0]: https://github.com/suitenumerique/people/releases/v1.19.0
[1.18.2]: https://github.com/suitenumerique/people/releases/v1.18.2
[1.18.1]: https://github.com/suitenumerique/people/releases/v1.18.1
[1.18.0]: https://github.com/suitenumerique/people/releases/v1.18.0
[1.17.0]: https://github.com/suitenumerique/people/releases/v1.17.0
[1.16.0]: https://github.com/suitenumerique/people/releases/v1.16.0
[1.15.0]: https://github.com/suitenumerique/people/releases/v1.15.0
[1.14.1]: https://github.com/suitenumerique/people/releases/v1.14.1
[1.14.0]: https://github.com/suitenumerique/people/releases/v1.14.0
[1.13.1]: https://github.com/suitenumerique/people/releases/v1.13.1
[1.13.0]: https://github.com/suitenumerique/people/releases/v1.13.0
[1.12.1]: https://github.com/suitenumerique/people/releases/v1.12.1
[1.12.0]: https://github.com/suitenumerique/people/releases/v1.12.0
[1.11.0]: https://github.com/suitenumerique/people/releases/v1.11.0
[1.10.1]: https://github.com/suitenumerique/people/releases/v1.10.1
[1.10.0]: https://github.com/suitenumerique/people/releases/v1.10.0
[1.9.1]: https://github.com/suitenumerique/people/releases/v1.9.1
[1.9.0]: https://github.com/suitenumerique/people/releases/v1.9.0
[1.8.0]: https://github.com/suitenumerique/people/releases/v1.8.0
[1.7.1]: https://github.com/suitenumerique/people/releases/v1.7.1
[1.7.0]: https://github.com/suitenumerique/people/releases/v1.7.0
[1.6.1]: https://github.com/suitenumerique/people/releases/v1.6.1
[1.6.0]: https://github.com/suitenumerique/people/releases/v1.6.0
[1.5.0]: https://github.com/suitenumerique/people/releases/v1.5.0
[1.4.1]: https://github.com/suitenumerique/people/releases/v1.4.1
[1.4.0]: https://github.com/suitenumerique/people/releases/v1.4.0
[1.3.1]: https://github.com/suitenumerique/people/releases/v1.3.1
[1.3.0]: https://github.com/suitenumerique/people/releases/v1.3.0
[1.2.1]: https://github.com/suitenumerique/people/releases/v1.2.1
[1.2.0]: https://github.com/suitenumerique/people/releases/v1.2.0
[1.1.0]: https://github.com/suitenumerique/people/releases/v1.1.0
[1.0.2]: https://github.com/suitenumerique/people/releases/v1.0.2
[1.0.1]: https://github.com/suitenumerique/people/releases/v1.0.1
[1.0.0]: https://github.com/suitenumerique/people/releases/v1.0.0
