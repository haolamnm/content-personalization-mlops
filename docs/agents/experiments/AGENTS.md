---
title: "Experiments"
id: agents-experiments-map
date: 2026-08-25
type: guide
status: active
tags: [experiments]
related:
  - ../AGENTS.md
---

# `docs/agents/experiments/`

One file per experiment: protocol, baseline, measured results, verdict. Lands here when the [`experiment`](../../../.agents/skills/) skill runs an isolated benchmark or model comparison (expected from Phase 2 training work onward).

## Contract

- Filename: `YYYY-MM-DD-slug.md` — the date says when it ran; findings that stay true graduate into `knowledge/`.
- Numbers or it didn't happen: every claim carries the measured value and the command that produced it.
- A negative result is a result — record what was tried and why it lost.

*No experiments recorded yet.*
