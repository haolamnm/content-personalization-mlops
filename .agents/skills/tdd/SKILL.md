---
name: tdd
description: Test-driven development workflow. Use when building features or fixing defects test-first, following red-green-refactor at public seams.
---

# Test-Driven Development (TDD)

Execute the Red → Green → Refactor loop at well-defined public seams to produce robust, regression-resistant tests.

## The Seam Principle

- **Test at Public Seams**: verify observable behavior through public interfaces — a service's API contract, a module's exported functions, a Kafka topic's output — never private helpers.
- **Survives Internal Refactoring**: if the retrieval service's internals are rewritten in place but its response contract holds, the tests pass unchanged.
- **Agree on Seams First**: clarify the seam under test before writing test cases; cross-language seams are the contract artifacts ([ADR 0004](../../../docs/adr/0004-polyglot-language-per-concern.md)), so contract tests come before client code.

## The TDD Loop

1. **Red (Write Failing Test)**: unit test beside the module, or integration case through the public entrypoint. Run it and verify it fails for the expected reason.
2. **Green (Minimal Implementation)**: implement the minimum code to pass; no unrequested features or speculative optimizations.
3. **Refactor (Clean Code & Invariants)**: improve naming, add *why* comments sparingly, then run the full language gate (`.agents/rules/verify-before-done.md`).

## Anti-Patterns to Avoid

- **Mocking Internals**: don't stub private functions; test through the module's public interface or the wire contract.
- **Testing Types**: don't write runtime tests for what the type system already proves (Rust/TypeScript especially).
- **Real Time & Real Sleeps in Tests**: inject clocks; never `sleep()` to wait for behavior — see `rust-testing` / `go-project-and-testing`.
- **Live Infra in Unit Scope**: broker-backed tests are tagged integration tests honoring [`resource-budget`](../../../.agents/rules/resource-budget.md).
