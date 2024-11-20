# Changelog

## [0.5.0] - 2024-11-20
### Added
- Pathlib support.

## [0.4.1] - 2024-11-14
### Improvement
- Documentation for the `cshelve` package.

## [0.4.0] - 2024-11-12
### Breaking Change
- The `azure-blob` is not installed by default. To install it, use `pip install cshelve[azure-blob]`.

### Added
- Added a development container for streamlined development.
- Introduced `ConfigurationError` exception for handling provider configuration errors.
- Initialized project documentation.

## [0.3.0] - 2024-11-08
### Added
- In-memory provider

### Improvement
- Tests refactored.
- Use in-memory provider for unit tests.
- Run examples in the CI pipeline.

## [0.2.2] - 2024-11-03
### Added
- Authentication methods for the azure-blob provider:
    - Anonymous read-only access on public blob storage.
    - Using Access key.

## [0.2.1] - 2024-11-02
### Improvement
- Interfaced with cloud provider modules.
- Added unit tests for the azure-blob provider.

## [0.2.0] - 2024-10-30
### Added
- Performance tests were added to the project. See [main.py](./performances/) for details.

### Changed
- **Breaking Change**: The provider `azure` in the `.ini` configuration has been renamed to `azure-blob`.

### Improved
- Improved the `n` flag to remove database content quicker using parallelism.

## [0.1.0] - 2024-10-24
- Initial release.
