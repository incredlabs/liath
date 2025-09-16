# Roadmap and TODO

This document tracks prioritized work items for Liath. It is intended to guide development and set expectations.

## High Priority

- Core vector search APIs beyond embedding generation
- Transaction semantics for LevelDB (or clearly document RocksDB-only)
- Connection management for concurrency (pooling)
- Indexing primitives for faster queries

## Security

- Role-based access control
- Session/token auth for HTTP API; enforce on `/query`
- API key support and rate limiting
- Input validation and sanitization across boundaries

## Plugin System

- Plugin lifecycle and configuration
- Documentation and examples for each plugin

## Storage Improvements

- Emulated column families for LevelDB
- Compression options and encryption-at-rest
- Data partitioning strategies

## CLI and HTTP

- CLI history persistence and auto-completion
- Script execution support
- HTTP request/response validation, better error contracts

## Docs and Examples

- Comprehensive API docs
- Tutorials and usage examples
- Plugin development guide

## Testing

- Unit tests for core components
- Integration tests
- Performance benchmarks

## Deployment

- Dockerfile and CI setup for tests
- Kubernetes manifests (optional)
- Automated backup scheduling and health checks
