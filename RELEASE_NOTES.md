# Frequenz Assets API Client Release Notes

## Summary

This release introduces a Assets API client with CLI support for interacting with Frequenz microgrid assets. It provides comprehensive electrical components functionality including batteries, EV chargers, inverters, and grid connection points, with enhanced type safety and error handling.

## New Features

* **Assets API Client**:
  * `list_electrical_components()` method for retrieving electrical components in a microgrid

* **Electrical Components Support**: Comprehensive data classes for electrical components
  * `ElectricalComponent` with category-specific information for batteries, EV chargers, inverters, grid connection points, and power transformers
  * Battery types: Li-ion, Na-ion with proper enum mapping
  * EV charger types: AC, DC, Hybrid charging support
  * Operational lifetime tracking and metric configuration bounds

* **Command-Line Interface**:
  * `assets-cli electrical-components <microgrid-id>` command

* **Type System**: Enhanced data classes with protobuf integration
  * `Microgrid`, `DeliveryArea`, `Location`, and comprehensive electrical component types
  * Proper enum mapping: `BatteryType`, `EvChargerType`, `InverterType`, `Metric`

## Bug Fixes
