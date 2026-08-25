---
description: Concurrency and HTTP-service discipline for Go — context propagation, goroutine leaks, graceful shutdown
globs: ["**/*.go"]
alwaysApply: false
---

# Rule: Go Concurrency & Services

## Constraints

- **context.Context is the first parameter** of every request-path call — cancellation and deadlines propagate from the HTTP request through Kafka produce to the response; bare `context.Background()` inside handlers is banned.
- **No goroutine without an exit**: every `go func()` has a documented stop path (context cancel, channel close, or `errgroup`); starting goroutines in library code without ownership transfer is banned.
- **Timeouts everywhere**: every outbound call (HTTP client, Kafka producer) sets an explicit timeout — zero-value clients are banned.
- **Graceful shutdown is part of the service**: signal handling drains in-flight requests and flushes producers before exit; SIGKILL losing events is acceptable, SIGTERM losing them is not.
- **Back-pressure at ingestion**: the event gateway applies bounded queues/load-shedding under load and returns 429s — unbounded buffering that turns slow consumers into OOM is banned.
- Handlers stay thin: decode → validate against schema → hand to a testable core; business logic never lives inside HTTP handler bodies.
