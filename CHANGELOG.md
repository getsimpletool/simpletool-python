# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [SimpleTool](https://github.com/nchekwa/simpletool-python/tree/master).

## [0.0.4] - 2025-01-02

### Fixed
- select_random_api_key where value is empty string cause error

### Added

- add proper validation of run/execute output type (validate_tool_output decorator)
this will allow only to use as output: Union[List[ContentT], ErrorData]
where: ContentT = TypeVar('ContentT', ImageContent, TextContent, EmbeddedResource)

## [0.0.3] - 2025-01-02

### Fixed
- upgrade to 0.0.2 breaks loading of tool (#1).

### Added
- run test now will now run Autopep8 to fix some formating issues and Flake8 linting on test files

## [0.0.2] - 2025-01-02

### Added

- documentation in README.md
- run_test.py - manual run test

### Changed

- fix some formating flake8 comp
- autorun github workflow on change version in setup.py

## [0.0.1] - 2025-01-01

### Added

- Init project
- This CHANGELOG file to hopefully serve as an evolving example of a
  standardized open source project CHANGELOG.


[0.0.1]: https://github.com/nchekwa/simpletool-python/releases/tag/v0.0.1