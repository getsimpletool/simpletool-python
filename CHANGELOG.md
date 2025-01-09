# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [SimpleTool](https://github.com/nchekwa/simpletool-python/tree/master).


# [0.0.14] - 2025-01-09 Milestone Alpha2

## Added
- SimpleToolResponseModel
- add correct handle __repr__ for SimpleTool child classes
- add get_version for `setup.py` to automate version update
- auto add annotation version in `__init__.py`

# [0.0.13] - 2025-01-08 Milestone Alpha2

## Fixed
- Updated test import from `BoolContents` to `BoolContent` to match type definition


# [0.0.12] - 2025-01-08 Milestone Alpha2

### Added
- added `input_model` will be mandatory - as mapping SimpleInputModel to SimpleTool
- `input_schema` will be from now generated based on `input_model` (and will not be able to be ovveriden)
- added `output_model` + `output_schema` will be generated based on return type of `run` method
- types for return (1 base + 6 subclasses):
  - Content - base class
  - TextContent - for text based content
  - ImageContent - for image based content
  - FileContent - for file based content
  - ResourceContent - for resource based content
  - BoolContent - for boolean based content
  - ErrorContent - for error based content


# [0.0.10] - 2025-01-06 Milestone Alpha

### Added
- ready to use own SimpleTool class naming convention
- added empty __main__ to load module smoothly w/o any errors
- adding a context manager for resource cleanup (auto clean in __aexit__ method)
- implement timeout mechanisms for long-running tools
- remove `execute` def option from Tool class - make it SIMPLE -> handled by `run` method option (only)
- added own SimpleInputSchema class which is used to extract json schema from input types
- by default json schema extraction for SimpleInputSchema will remove `title` and `description` fields

## [0.0.7] - 2025-01-05

### Added
- test which cover decorator @validate_tool_output - used to check if users return only valid list of elements types
- added FileContent which return encoded base64 file content and mime of this file
- added in ResourceContents mandatory `name` attribute and optional `description` attribute - as server needs to be able to identify resource also by the `name` (which will work as `id` in database)

### Fixed
- run/execute should return Sequence (which is covariant) instead of List (which is invariant) - that should fully allow return mix of types with no linter warnings

## [0.0.6] - 2025-01-04

### Added
- allow List of mixtures of ContentT to be returned from tool

## [0.0.5] - 2025-01-03

### Fixed
- tool should from now always return list of elements - List[ContentT]

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