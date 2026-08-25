---
title: MLOps Zero→Hero Docs — Hub
id: docs-hub
date: 2026-08-25
type: index
status: active
tags: [mlops, documentation-hub]
related:
  - ./index.json
---

# Documentation Hub

Durable documentation for the Zero→Hero workspace. Learning-in-progress material stays in `.notes/` (local-only); everything publishable lives here. Machine catalogs: [`index.json`](./index.json) is generated — regenerate after doc changes (`python3 scripts/gen_docs_metadata.py`), never hand-edit.

## Architecture Decision Records (`docs/adr/`)

Binding decisions with alternatives; newest supersedes oldest explicitly. Catalog: [`adr/index.json`](./adr/index.json) (generated).

- [`0001-content-personalization-theme.md`](./adr/0001-content-personalization-theme.md): the carrying theme and why IoT lost.
- [`0002-local-learning-and-reference-layout.md`](./adr/0002-local-learning-and-reference-layout.md): `.notes/`/`.repos/` stay gitignored by design.
- [`0003-ram-budgeted-local-infrastructure.md`](./adr/0003-ram-budgeted-local-infrastructure.md): RAM reality — compose profile groups, one at a time.
- [`0004-polyglot-language-per-concern.md`](./adr/0004-polyglot-language-per-concern.md): Java 25 / Python 3.14 / Go 1.27 / Rust 1.98 / TS+SvelteKit ownership map.
- [`0005-sveltekit-over-nextjs.md`](./adr/0005-sveltekit-over-nextjs.md): optimized FE choice with rejected alternatives.

## Research & Decision Log (`docs/agents/`)

Agent docs: [`agents/README.md`](./agents/README.md) (knowledge / runbooks / experiments map). Catalog (research notes use `NNNN-slug.md`, landing as Phase 0 study output): [`agents/index.json`](./agents/index.json) (generated).

## Agent Layer

- [`../AGENTS.md`](../AGENTS.md): instruction hierarchy, principles, stack, verification gates.
- [`../CONTEXT-MAP.md`](../CONTEXT-MAP.md): bounded contexts and ubiquitous language.
- [`../.agents/rules/`](../.agents/rules/): operational rules (frontmattered); language-specific sets under `java-*`, `go-*`, `rust-*`, `python-*`.
- [`../.agents/skills/`](../.agents/skills/): phase workflows — `studying-mlops`, `managing-mlops-services`, plus the ported craft set (`implement`, `tdd`, `codebase-review`, …).
