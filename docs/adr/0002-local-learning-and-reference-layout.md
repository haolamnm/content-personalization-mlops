---
title: "ADR 0002 — Local-Only Learning Layer (.notes/, .repos/)"
id: adr-0002
date: 2026-08-24
type: adr
status: accepted
tags: [layout, git, learning]
related:
  - ./0001-content-personalization-theme.md
---

# ADR 0002 — Local-Only Learning Layer (.notes/, .repos/)

## Status

Accepted (2026-08-24).

## Context

Learning notes and third-party reference clones are personal working material, but this repository will be presented publicly at the end of the journey. Mixing scratch notes and vendored upstream code into a portfolio repo pollutes both.

## Decision

`.notes/` (roadmap, topic walkthroughs) and `.repos/` (reference clones + generated `metadata.json`) are **gitignored local directories**, permanent residents by convention. The tracked context layer (`AGENTS.md`, `CONTEXT-MAP.md`, `docs/`) indexes them so any agent on this machine finds them, without publishing them.

## Alternatives Considered

1. **Track `.notes/`**: rejected — half-finished personal notes would ship to the public repo.
2. **Git submodules for references**: rejected — clones are read-only study material, not dependencies; submodules add workflow friction for zero benefit.
3. **Track only metadata.json inside .repos/**: considered; kept simple — the generator + curated registry live tracked under `scripts/`, so provenance is reproducible even though the JSON output is local ([generated-artifacts rule](../../.agents/rules/generated-artifacts.md)).

## Consequences

- Cloning this repo elsewhere loses notes/clones; `scripts/gen_repos_metadata.py --check` plus the registry make restoration mechanical.
- Never stage `.notes/*` or `.repos/*`; enforced by `.gitignore` and the directory contract in AGENTS.md §6.
