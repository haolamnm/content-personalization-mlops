---
description: General Go rules for the event gateway, BFF, and simulators — umbrella entry; specifics live in go-*.md siblings
globs: ["**/*.go", "**/go.mod", "**/go.sum"]
alwaysApply: false
---

# Go General Rules

Go owns the edge: the event gateway, the app-facing BFF, and simulators/load generators ([ADR 0004](../../docs/adr/0004-polyglot-language-per-concern.md)). Umbrella entry — read the sibling matching your change:

| Sibling | Covers |
|:---|:---|
| [`go-concurrency-and-services.md`](./go-concurrency-and-services.md) | Context propagation, goroutine exits, timeouts, graceful shutdown, back-pressure |
| [`go-project-and-testing.md`](./go-project-and-testing.md) | Module layout, adapter seams, table-driven + tagged integration tests |

## Universal Constraints

- **Stdlib first**: `net/http`, `encoding/json`, `log/slog` cover nearly everything; a dependency needs a reason written next to it in `go.mod`.
- **Errors are values**: wrap with `%w` and add context at each boundary; `errors.Is/As` for inspection; panics only for programmer errors.
- **Go 1.27** from `.computers/MACBOOK.md`; toolchain pinned via `go` directive in `go.mod`.
- `go vet` + `gofmt -l` clean before delivery (`verify-before-done` gate); module data lives under XDG paths per `.computers/MACBOOK.md` §4 — never `~/go`.
