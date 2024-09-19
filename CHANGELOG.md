# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


### Added

- ✨(domains) add endpoint to list and retrieve domain accesses #404
- 🍱(dev) embark dimail-api as container #366
- ✨(dimail) allow la regie to request a token for another user #416 
- ⚗️(frontend) show username on AccountDropDown #412

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

[unreleased]: https://github.com/numerique-gouv/people/compare/v1.1.0...main
[1.1.0]: https://github.com/numerique-gouv/people/releases/v1.1.0
[1.0.2]: https://github.com/numerique-gouv/people/releases/v1.0.2
[1.0.1]: https://github.com/numerique-gouv/people/releases/v1.0.1
[1.0.0]: https://github.com/numerique-gouv/people/releases/v1.0.0
