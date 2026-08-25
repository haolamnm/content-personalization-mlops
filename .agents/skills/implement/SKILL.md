---
name: implement
description: Implement features, bug fixes, or specifications following TDD, incremental verification, and surgical diffs.
---

# Implement Feature / Specification

Execute implementation tasks systematically from a specification, user request, or issue.

## Execution Sequence

1. **Orientation & Seams**:
   - Read [`CONTEXT-MAP.md`](../../../CONTEXT-MAP.md) and the owning bounded context; confirm language ownership ([ADR 0004](../../../docs/adr/0004-polyglot-language-per-concern.md)) before writing anything.
   - Find existing callers and tests with rg before writing anything.
   - Identify the public seam (contract artifact, API, topic) and verification criteria first.
2. **Incremental TDD Loop**:
   - Write a reproduction or behavior test at the seam (unit beside the module, integration against the contract).
   - Implement the minimal logic to satisfy it.
   - Run focused tests for just that module.
3. **Continuous Static Verification**: run the touched language's linter after touching signatures; fix warnings immediately (see `.agents/rules/<lang>-general.md`).
4. **Final Quality Check** (`.agents/rules/verify-before-done.md`): full gate for every touched language + generators' `--check`.
5. **Clean Handoff**:
   - Concise inline comments only where an invariant needs a *why*.
   - Update affected docs (CONTEXT-MAP rows, decision log) — see `.agents/rules/keep-docs-alive.md`.
