# Frequenz Assets API Client Release Notes

## Summary

This release introduces a complete Assets API client with CLI support for interacting with Frequenz microgrid assets, including comprehensive error handling and type safety.

## Upgrading

**Breaking Changes:**

- Added new required dependencies: `frequenz-api-assets`, `frequenz-api-common`, `frequenz-client-base`, `grpcio`

**CLI Support:**
Install with `pip install "frequenz-client-assets[cli]"` for command-line functionality.

## New Features

**Assets API Client:**

- Complete gRPC client for Frequenz Assets API
- Extends `BaseApiClient` for authentication and connection management
- `get_microgrid_details()` method for retrieving microgrid information

**Command-Line Interface:**

- `python -m frequenz.client.assets microgrid <id>` command
- Environment variable support for API credentials
- JSON output formatting

**Type System:**

- `Microgrid`, `DeliveryArea`, and `Location` data classes
- Protobuf integration with proper type safety

**Exception Handling:**

- Custom exception hierarchy (`AssetsApiError`, `NotFoundError`, `AuthenticationError`, `ServiceUnavailableError`)
- JSON serialization support for error responses

## Bug Fixes

- Improved dependency management with optional dependency groups
- Enhanced gRPC error handling and type safety
- Cleaned up deprecated code
