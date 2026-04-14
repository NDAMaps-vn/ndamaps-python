# Changelog

## 0.1.0 (2026-04-14)


### Features

* **navigation:** add optimized_route SDK method ([e94bb36](https://github.com/NDAMaps-vn/ndamaps-python/commit/e94bb36af21ca068218cd2ef3dd2f29c36366328))
* **python:** initial Python SDK implementation based on TypeScript version ([202b71a](https://github.com/NDAMaps-vn/ndamaps-python/commit/202b71a9f5ca2411add10770e5128e6b703d8321))


### Bug Fixes

* **maps:** update map tiles base url to maptiles.ndamaps.vn ([2bc5dc2](https://github.com/NDAMaps-vn/ndamaps-python/commit/2bc5dc200d33fe9453d1e6c1b1a39db516d7c826))
* revert TILES_BASE to maptiles.ndamaps.vn + fix CI errors ([87078b9](https://github.com/NDAMaps-vn/ndamaps-python/commit/87078b92a90e5f27cb78ef4213c5461608ac3ebd))

## 0.1.0 (Unreleased)

### Features

* Initial release of NDAMaps Python SDK
* Places module: autocomplete, place detail, children, nearby
* Geocoding module: forward and reverse geocoding
* Navigation module: directions, distance matrix, optimized route
* Maps module: static map URL builder
* NDAView module: street-level imagery search
* Forcodes module: encode/decode geographic coordinates
* Session token manager for billing optimization
* Automatic retry with exponential backoff
