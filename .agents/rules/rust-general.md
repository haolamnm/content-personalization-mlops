---
description: General Rust rules for the retrieval/ranking hot path — umbrella entry; specifics live in rust-*.md siblings
globs: ["**/*.rs", "**/Cargo.toml", "**/Cargo.lock"]
alwaysApply: false
---

# Rust General Rules

Rust owns the retrieval/ranking hot path ([ADR 0004](../../docs/adr/0004-polyglot-language-per-concern.md)): Redis feature join + light scoring under a measured tail-latency budget. Umbrella entry — read the sibling matching your change:

| Sibling | Covers |
|:---|:---|
| [`rust-types-and-error-handling.md`](./rust-types-and-error-handling.md) | Newtype IDs at seams, enum state, thiserror/anyhow split |
| [`rust-async-and-latency.md`](./rust-async-and-latency.md) | Tokio discipline, cancellation safety, latency budgets |
| [`rust-testing.md`](./rust-testing.md) | Deterministic tests, property tests for scoring |

## Universal Constraints

- The hot path is the reason Rust exists here — never accept an allocation, clone, or lock in the request loop without a measurement justifying it.
- Latency and memory claims come from `criterion` benches / recorded profiles into `COMPUTER.md` §5, never intuition ([Principle 5](../../AGENTS.md)).
- `cargo fmt` + zero-warning `cargo clippy` before delivery (`verify-before-done` gate).
- Edition 2024, stable toolchain (pinned in `COMPUTER.md`); nightly only behind an ADR.
