---
description: Project layout and testing conventions for Go services — table-driven tests, integration seams
globs: ["**/*.go"]
alwaysApply: false
---

# Rule: Go Layout & Testing

## Constraints

- **One service, one module**: `platform/services/<name>/` is its own Go module with `cmd/<name>/main.go` as the only entrypoint; shared code lives in small internal packages, never a grab-bag `utils`.
- **Ports and adapters lightly**: Kafka producer, HTTP client, and clock sit behind small interfaces so tests inject fakes — but only where tests need them; speculative interfaces are banned.
- **Table-driven tests** are the default shape; every error branch gets a case.
- **Integration tests are tagged** (`//go:build integration`) and require running infra — they respect [`resource-budget`](./resource-budget.md) (one compose group) and skip cleanly otherwise.
- Load generators/simulators are real services with their own module, not scripts — they get versioned, logged, and reused across phases.
