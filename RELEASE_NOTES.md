# Frequenz Assets API Client Release Notes

## Upgrading

- Bumped `frequenz-api-common` from `v0.8.9` to `v0.8.11` and `frequenz-api-assets` from `v0.3.0` to `v0.4.0`.
- Renamed `MarketLocation` to `MarketLocationRef` to match the upstream protobuf rename in `frequenz-api-common` v0.8.11. The `market_location_from_proto` helper was renamed to `market_location_ref_from_proto` accordingly.
- Renamed the `MarketTopologyRelation.market_location` field to `market_location_ref` to match the upstream protobuf field rename in `frequenz-api-assets` v0.4.0.
