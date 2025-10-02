# Changelog

## [unreleased]

## [1.1.0]

- Added support for building documentation in Read the Docs (it requires exporting
  environment variable `VHS_NO_SANDBOX=true`).

- Migrated documentation to Read the Docs.

- Moved repository to [sphinx-contrib](https://github.com/sphinx-contrib) organization.

## [1.0.1]

- Fix issue with GIFs being inappropriate deleted on partial rebuild.

## [1.0.0]

- Initial release.

## [1.0.0-beta0]

- Added `max_version` parameter.

- Improved detection of changes in VHS files.

- Delayed cleaning up old GIFs by `vhs_cleanup_delay`, 1 day by default.

- Plugin can now detect circular `Source` commands.

- Updated CI and dependencies.

[unreleased]: https://github.com/sphinx-contrib/vhs/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/sphinx-contrib/vhs/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/sphinx-contrib/vhs/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/sphinx-contrib/vhs/compare/v1.0.0-beta0...v1.0.0
[1.0.0-beta0]: https://github.com/sphinx-contrib/vhs/compare/v0.0.4...v1.0.0-beta0
