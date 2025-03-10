# Changelog

All notable changes to this project will be documented in this file.

## [0.2.3](https://github.com/wlad031/shoutrrr-web/releases/tag/v0.2.3) - 2025-02-23

### Changed
- Escaping for special characters in Telegram MarkdownV2 messages: added `(` and `)` characters.

## [0.2.2](https://github.com/wlad031/shoutrrr-web/releases/tag/v0.2.2) - 2025-02-21

This release doesn't bring significant changes, just a little bit better logging and refactoring.

## [0.2.1](https://github.com/wlad031/shoutrrr-web/releases/tag/v0.2.1) - 2025-02-18

### Added
- Escaping for special characters in Telegram MarkdownV2 messages

## [0.2.0](https://github.com/wlad031/shoutrrr-web/releases/tag/v0.2.0) - 2025-02-18

Since I'm made changes in [common-python](https://github.com/wlad031/common-python) library, the same applies here.

### Added
- Authentication can now be disabled by setting `AUTH_ENABLED` environment variable to `false` (default).

### Deprecated
- `X-Api-Key` header is deprecated in favor of `Authorization` header with `token api_key` format

## [0.1.0](https://github.com/wlad031/shoutrrr-web/releases/tag/v0.1.0) - 2025-02-12

### Added
- Initial release of shoutrrr-web
- Flask-based web interface for Shoutrrr
- RESTful API endpoint `/send` for sending notifications
- Support for multiple notification services via YAML configuration
- Tag-based notification routing
- API key authentication
- Health check endpoint `/health`
- Docker support with health checks
- Environment variable configuration
- Example configuration files
