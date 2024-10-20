Tests are divided into three parts:
- integration: Contains integration tests for cloud providers.
- sequential: Contains integration tests for cloud providers that cannot run in parallel as tests on the `__len__` operator.
- unit: Contains unit tests that are agnostic of cloud providers as tests on the interface.
