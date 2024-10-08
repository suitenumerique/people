# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- 🐛(frontend) fix update accesses form #448

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

[unreleased]: https://github.com/numerique-gouv/people/compare/v1.2.1...main
[1.2.1]: https://github.com/numerique-gouv/people/releases/v1.2.1
[1.2.0]: https://github.com/numerique-gouv/people/releases/v1.2.0
[1.1.0]: https://github.com/numerique-gouv/people/releases/v1.1.0
[1.0.2]: https://github.com/numerique-gouv/people/releases/v1.0.2
[1.0.1]: https://github.com/numerique-gouv/people/releases/v1.0.1
[1.0.0]: https://github.com/numerique-gouv/people/releases/v1.0.0
