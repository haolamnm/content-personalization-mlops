---
name: handoff
description: Compact the current session context into a durable handoff so a cold agent (or human) can resume without loss.
---

# Handoff Session

Produce a compact, self-contained handoff at the end of a session or before switching context.

## Execution Sequence

1. **Update FOCUS.md**: goal, checklist state (verified only), decisions & dead ends with evidence, blockers.
2. **Update the doc layer**: any fact that changed — decision-log rows in [`docs/agents/decision-log.md`](../../../docs/agents/decision-log.md), roadmap checkboxes, CONTEXT-MAP Implemented-vs-Reserved status.
3. **Verify claims**: every "done" in the handoff traces to a command that was actually run and green (language gates per `verify-before-done`).
4. **Name the next step**: the first action for the next session, stated concretely ("run `studying-mlops` on purchase-prediction-mlops", not "continue studying").
5. **Keep it compact**: target < 60 lines; link to docs instead of duplicating them.

Bound by `.agents/rules/keep-docs-alive.md`.
