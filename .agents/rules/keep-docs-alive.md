---
description: Docs evolve atomically with work — indexes, decision log, roadmap, and CONTEXT files stay in lockstep
globs: ["**/*.md"]
alwaysApply: true
---

# Rule: Keep Docs Alive

Documentation drift is a defect: the next agent trusts whatever it reads first.

## Constraints

- **Atomic updates**: a change that alters facts updates every dependent doc in the same change — CONTEXT-MAP rows, the relevant `docs/agents/knowledge/` note (and an ADR when the change is architectural), `.notes/00-roadmap.md` checkboxes, module `CONTEXT.md` (once modules exist).
- **Indexes are contracts**: adding/removing/renaming any note, ADR, skill, rule, or clone updates its index — AGENTS.md mappings, docs/AGENTS.md, the generated `docs/**/index.json` (regenerate via script), repos registry.
- **Decision log is append-only**: new decisions get dated rows; corrections append a superseding row rather than rewriting history.
- **Implemented vs Reserved stays honest**: CONTEXT-MAP §4 reflects what actually runs — never upgrade "reserved" to "implemented" until execution proves it ([verify-before-done](verify-before-done.md)).
