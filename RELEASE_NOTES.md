# Frequenz Assets API Client Release Notes

## New Features

- Electrical components now expose `operational_mode` with the requested mode
  returned by Assets v0.1.1. Known values use `ElectricalComponentOperationalMode`;
  unknown values remain integers. The default is `UNSPECIFIED` when the server
  does not supply a mode. This value does not confirm that the mode is applied.
