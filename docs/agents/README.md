---
title: "Agents Docs Map"
id: agents-docs-map
date: 2026-08-25
type: guide
status: active
tags: [docs, layout]
related:
  - ../README.md
---

# `docs/agents/` — what lives where

Agent-facing documentation, split by *what kind of reading* it is. Everything here carries frontmatter and lands in the generated [`index.json`](./index.json) (source of truth is each file's frontmatter; never hand-edit the index).

| Section | Answers | Shape |
|:---|:---|:---|
| [`knowledge/`](./knowledge/) | "How does X work here and what bit us?" | topical notes: pins, contracts, constraints, gotchas |
| [`runbooks/`](./runbooks/) | "What exact steps do I run?" | executable procedures with verification at each step |
| [`experiments/`](./experiments/) | "What did we try and what came out?" | protocol + measured results per experiment |

## Conventions

- **Knowledge over log**: durable, self-contained, kept current — no numbered prefixes, no append-only diaries. When a fact changes, edit the note.
- **Architectural decisions** (with alternatives weighed) graduate into [`docs/adr/`](../adr/) — this tree links to them, never restates them.
- **Milestone status** ("X is live on Y") belongs to CONTEXT-MAP rows and module CONTEXT.md files, not here.
- New section types must be added to this map in the same change (keep-docs-alive).
