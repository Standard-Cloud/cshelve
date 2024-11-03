# Changelog

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
