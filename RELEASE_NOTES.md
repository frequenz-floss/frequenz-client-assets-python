# Frequenz Assets API Client Release Notes

## New Features

The client methods now accept an optional `raise_on_error` argument. When set to `True`, the client will raise a exceptions for any entity that doesn't pass validation instead of filtering out unvalid entities and returning only valid ones (which is still the default).
