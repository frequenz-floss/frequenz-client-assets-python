# Frequenz Assets API Client Release Notes

## Summary

This release adds support for retrieving microgrid electrical component connections through a new client method and CLI command.

## Upgrading

- The `get_microgrid` and `list_microgrid_electrical_components` methods now expect an argument of type `MicrogridId`, instead of an `int`.
- The `PvInverter` type has been renamed to `SolarInverter`, to be compatible with the microgrid api client.

## New Features

- This exposes the abstract `Battery`, `EvCharger` and `Inverter` types.

### Component Connections API

* **New `ComponentConnection` class**: Introduced to represent connections between electrical components in a microgrid
* **New client method**: Added method to retrieve microgrid electrical component connections
* **CLI command extension**: Added `component-connections` command to list component connections

## Bug Fixes

<!-- No bug fixes in this release -->
