# Frequenz Assets API Client Release Notes

## New Features

- Electrical components now provide `provides_telemetry()` and `accepts_control()`
  to interpret the requested operational mode. Both methods raise `ValueError`
  for unspecified or unrecognized modes. These results describe the requested
  configuration, not the device's current state.
