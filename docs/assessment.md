# Project Assessment

Liath is a Lua-queryable key–value database with pluggable storage backends and a plugin system. This assessment summarizes the current state, key gaps, and recommended next steps.

## Current State

- Storage backends: RocksDB and LevelDB
- Lua query execution via `lupa`
- Plugin architecture (file, LLM, embeddings, vector DB, caching, monitoring, backup)
- CLI and HTTP server
- Namespace support and LuaRocks module trees per namespace

## Notable Gaps

- Security: plaintext password legacy, no auth on HTTP `/query`, no rate limiting
- Packaging: optional heavy deps should be extras (addressed)
- Plugin exposure and imports (addressed)
- Lua pathing inconsistencies (addressed)
- Testing/CI: limited automated tests, no CI workflow
- Operationalization: no Dockerfile; setup script assumes `sudo`

## Recommendations

- Enforce auth on HTTP API; add sessions/tokens and rate limiting
- Add CI for tests; include Dockerfile for reproducible builds
- Expand tests for storage, Lua runtime, and plugins
- Improve docs and examples; clarify optional features
