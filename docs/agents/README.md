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

Agent-facing documentation, split by *what kind of reading* it is. Everything here carries frontmatter and lands in the generated [`index.json`](./index.json); architecture also has a focused generated [`architecture/index.json`](./architecture/index.json) for selective loading (source of truth is each file's frontmatter; never hand-edit an index).

| Section | Answers | Shape |
|:---|:---|:---|
| [`knowledge/`](./knowledge/) | "How does X work here and what bit us?" | topical notes: pins, contracts, constraints, gotchas |
| [`runbooks/`](./runbooks/) | "What exact steps do I run?" | executable procedures with verification at each step |
| [`experiments/`](./experiments/) | "What did we try and what came out?" | protocol + measured results per experiment |
| [`architecture/`](./architecture/) | "What are we building and which choices are still open?" | north-star vision + provisional design board |

## Conventions

- **Knowledge over log**: durable, self-contained, kept current — no numbered prefixes, no append-only diaries. When a fact changes, edit the note.
- **Architecture before ADR**: use `architecture/` to explore candidates and evidence; graduate a choice to `docs/adr/` only after its decision gate is satisfied.
- **Selective loading**: read a section index first and load only the documents needed for the question; do not concatenate the whole docs tree into agent context.
- **Architectural decisions** (with alternatives weighed) graduate into [`docs/adr/`](../adr/) — this tree links to them, never restates them.
- **Milestone status** ("X is live on Y") belongs to CONTEXT-MAP rows and module CONTEXT.md files, not here.
- New section types must be added to this map in the same change (keep-docs-alive).
