# Changelog

## [Unreleased]

## [1.4.0] - 2026-01-01

- Added support for rendering SVGs instead of GIFs via
  [a fork that supports it](https://github.com/agentstation/vhs/releases).
- Support for Sphinx 9.

## [1.3.0] - 2025-11-25

- Add `vhs_n_jobs` and `vhs_n_jobs_read_the_docs` config values.
- Changed log message from "Rendering VHS tapes" to "Rendering terminal GIFs" to avoid
  confusion for people who don't known the name of VHS project.

## [1.2.0] - 2025-10-12

- Forced parallel mode to 8 threads in readthedocs.

  Since readthedocs doesn't provide an easy way to enable parallel builds, Sphinx-VHS will
  default to 8 threads when running in readthedocs.

- Releases are no longer uploaded to test version of PyPi.

## [1.1.0] - 2025-10-03

- Added support for building documentation in Read the Docs (it requires exporting
  environment variable `VHS_NO_SANDBOX=true`).

- Migrated documentation to Read the Docs.

- Moved repository to [sphinx-contrib](https://github.com/sphinx-contrib) organization.

## [1.0.1] - 2025-10-01

- Fix issue with GIFs being inappropriate deleted on partial rebuild.

## [1.0.0] - 2025-09-30

- Initial release.

## [1.0.0-beta0] - 2025-09-30

- Added `max_version` parameter.

- Improved detection of changes in VHS files.

- Delayed cleaning up old GIFs by `vhs_cleanup_delay`, 1 day by default.

- Plugin can now detect circular `Source` commands.

- Updated CI and dependencies.

## [0.0.5] - 2024-11-18

## [0.0.4] - 2024-09-01

## [0.0.3] - 2024-08-27

## [0.0.2] - 2024-08-27

## [0.0.1] - 2023-06-30

[0.0.1]: https://github.com/sphinx-contrib/vhs/releases/tag/v0.0.1
[0.0.2]: https://github.com/sphinx-contrib/vhs/compare/v0.0.1...v0.0.2
[0.0.3]: https://github.com/sphinx-contrib/vhs/compare/v0.0.2...v0.0.3
[0.0.4]: https://github.com/sphinx-contrib/vhs/compare/v0.0.3...v0.0.4
[0.0.5]: https://github.com/sphinx-contrib/vhs/compare/v0.0.4...v0.0.5
[1.0.0]: https://github.com/sphinx-contrib/vhs/compare/v1.0.0-beta0...v1.0.0
[1.0.0-beta0]: https://github.com/sphinx-contrib/vhs/compare/v0.0.5...v1.0.0-beta0
[1.0.1]: https://github.com/sphinx-contrib/vhs/compare/v1.0.0...v1.0.1
[1.1.0]: https://github.com/sphinx-contrib/vhs/compare/v1.0.1...v1.1.0
[1.2.0]: https://github.com/sphinx-contrib/vhs/compare/v1.1.0...v1.2.0
[1.3.0]: https://github.com/sphinx-contrib/vhs/compare/v1.2.0...v1.3.0
[1.4.0]: https://github.com/sphinx-contrib/vhs/compare/v1.3.0...v1.4.0
[unreleased]: https://github.com/sphinx-contrib/vhs/compare/v1.4.0...HEAD
