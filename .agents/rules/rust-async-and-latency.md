---
description: Async discipline and latency budgets for the Rust hot path — cancellation safety, no blocking, measured p99
globs: ["**/*.rs"]
alwaysApply: false
---

# Rule: Rust Async & Latency

## Constraints

- **The budget is a contract**: the retrieval service declares a p99 target (set at Phase 4, measured thereafter); every dependency call carries a `tokio::time::timeout` shorter than what remains — unbounded awaits are banned.
- **Cancellation-safe patterns only**: use `select!` with futures that tolerate being dropped mid-flight; partial results degrade explicitly (see `rust-types-and-error-handling`), never silently.
- **No blocking on the runtime**: file/CPU-bound work (feature-vector assembly over large sets) goes through `spawn_blocking` or rayon — a blocked worker starving the accept loop is a defect.
- **Pipelined fetches**: Redis/Elasticsearch reads batch via pipelining/MGET-style calls; N sequential round-trips in the request path are banned without a recorded justification.
- **Measure before optimizing, after too**: any change touching the request loop ships with before/after criterion numbers appended to `.computers/MACBOOK.md` §5.
