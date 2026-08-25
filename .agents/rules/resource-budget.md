---
description: Machine RAM budget (see .computers/MACBOOK.md) — never run the whole stack; one profile group at a time, measured before and after
globs: ["**/docker-compose*.yml", "**/docker-compose*.yaml"]
alwaysApply: true
---

# Rule: Resource Budget

This machine's unified memory is small relative to the target stack (~20 services, several JVM-heavy). Full-stack startup is a guaranteed OOM — facts in [`.computers/MACBOOK.md`](../../.computers/MACBOOK.md), decision in [ADR 0003](../../docs/adr/0003-ram-budgeted-local-infrastructure.md).

## Constraints

- **One group at a time**: exactly one compose profile group runs (groups defined in ADR 0003 / `managing-mlops-services` skill); previous group is down before the next starts.
- **Preflight/postflight mandatory**: `memory_pressure | head -20` + `docker stats --no-stream` around any compose lifecycle; record actual RSS figures into the running box's fact file §5 — `.computers/MACBOOK.md` locally, `.computers/THINKBOOK.md` remotely ([platform/infra/CONTEXT.md](../../platform/infra/CONTEXT.md)).
- **Estimates are estimates**: planning budgets live in ADR 0003 until replaced by measurements; never cite them as fact.
- **Prefer low-RSS implementations** where we own code — language ownership already encodes this ([ADR 0004](../../docs/adr/0004-polyglot-language-per-concern.md)).
- **OrbStack memory is dynamic** (`.computers/MACBOOK.md` §3): set an explicit VM cap before heavy groups rather than trusting reclaim mid-run; do not change the cap without recording it in `.computers/MACBOOK.md` and the relevant knowledge note.
