---
name: experiment
description: Run isolated benchmark or model experiments against baselines and record outcomes in docs/agents/. Use when measuring a change's effect (latency, quality, cost) rather than asserting it.
---

# Run Experiment Series

Execute one isolated experiment against a recorded baseline — performance (latency/RAM), retrieval/model quality, or pipeline cost.

## Execution Sequence

1. **Pick & Read**: choose the experiment from its doc under `docs/agents/` (`NNNN-slug.md`); read the design and the success metric. If no doc exists, write one *first* — hypothesis, metric, baseline, stop condition.
2. **Baseline first**: capture current numbers before changing anything ([Principle 5](../../../AGENTS.md)); a comparison needs both arms measured, not remembered.
3. **One variable**: implement the single change under test; no stacked tweaks — confounded results are uninterpretable.
4. **Measure**: run the agreed harness/protocol; record environment facts (`COMPUTER.md`) alongside numbers so results are reproducible on this machine.
5. **Record same-session**: append results (numbers, setup, date, dead ends) to the experiment doc and add its catalog entry via `gen_docs_metadata.py`.
6. **Promote explicitly**: winners become binding only via a dated decision-log row in [`docs/agents/decision-log.md`](../../../docs/agents/decision-log.md); reversals of ADRs require a superseding ADR.

Bound by `.agents/rules/verify-before-done.md` and `resource-budget.md` (measurements respect group discipline).
