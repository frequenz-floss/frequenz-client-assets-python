# Frequenz Assets API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

## New Features

- Electrical components now provide `provides_telemetry()` and `accepts_control()`
  to interpret the requested operational mode. Both methods raise `ValueError`
  for unspecified or unrecognized modes. These results describe the requested
  configuration, not the device's current state.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
