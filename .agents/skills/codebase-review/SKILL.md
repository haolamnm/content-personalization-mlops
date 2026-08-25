---
name: codebase-review
description: Review changes since a fixed point along two axes — Standards (repo rules) and Spec (what the issue/decision asked for). Runs both reviews as parallel sub-agents and reports them side by side.
---

# Two-Axis Code Review

Review the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented rules?
- **Spec** — does it faithfully implement what was asked?

Both axes run as **parallel sub-agents** so they don't pollute each other's context; this skill aggregates.

## Process

### 1. Pin the fixed point

Commit SHA, branch, tag, `main`, `HEAD~5` — if unspecified, ask. Capture once: `git diff <fixed-point>...HEAD` (three-dot) plus `git log <fixed-point>..HEAD --oneline`. Confirm the ref resolves and the diff is non-empty before spawning anything.

### 2. Identify the spec source

In order: active goal in `.worklog/FOCUS.md` → decision-log rows / ADRs → roadmap phase deliverable → user-supplied path. If none exists, the Spec axis reports "no spec available".

### 3. Identify the standards sources

- `AGENTS.md` (+ `AGENTS.local.md`, `.computers/MACBOOK.md` facts), `CONTEXT-MAP.md`
- `.agents/rules/*.md` — general rules plus the touched language's set (`java-*`, `go-*`, `rust-*`, `python-*`), especially `minimal-footprint.md`, `resource-budget.md`
- The owning bounded context in CONTEXT-MAP §1 for seam boundaries

The Standards axis also carries the **Fowler smell baseline** (*Refactoring*, ch.3): labelled judgement calls, never hard violations; a documented repo rule overrides the baseline; skip anything language gates already enforce. Polyglot readings:

- **Primitive Obsession** — raw IDs/strings crossing seams where newtypes/enums belong (`rust-types-and-error-handling`; same discipline in TS/Java).
- **Duplicated Code / Data Clumps** — the same feature/context params travelling together; bundle into a typed struct.
- **Speculative Generality** — interfaces with one implementation; inline until a second arrives.
- **Shotgun Surgery / Divergent Change** — one pipeline stage scattered across files, or one file changing for unrelated reasons.
- **Contract drift** — code diverging from the OpenAPI/Avro artifact without regenerating it ([ADR 0004](../../../docs/adr/0004-polyglot-language-per-concern.md) consequences).

### 4. Spawn both sub-agents in parallel

- **Standards brief**: "(a) every diff violation of a documented standard — cite file + rule; (b) baseline smells — name + quote hunk. Hard violations vs judgement calls distinguished; repo rules override the baseline. Under 400 words."
- **Spec brief**: "(a) requirements missing or partial; (b) unrequested behavior (scope creep); (c) implemented but wrong. Quote the spec line per finding. Under 400 words."

If no spec exists, skip that sub-agent and note it.

### 5. Aggregate

Present under `## Standards` and `## Spec`, unmerged. One-line summary: findings per axis, worst issue *within* each axis — never a single cross-axis winner.

## Why two axes

Code can follow every rule yet implement the wrong thing (Standards pass, Spec fail), or do exactly what was asked while breaking conventions (Spec pass, Standards fail). Separate reporting stops either from masking the other.
