# Frequenz Assets API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

* Updated `frequenz-api-assets` to `0.3.0`, replacing the old `assets.v1`
  generated API with `platformassets.v1alpha1`.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

* Added client methods for the new `platformassets.v1alpha1` RPCs:
  `list_gridpools()`, `list_gridpool_energy_schedules()`,
  `list_market_topology_relations()`, `list_microgrids()`, and
  `list_microgrid_sensors()`.
* Added `component_ids` and `categories` filters to
  `list_microgrid_electrical_components()`.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
