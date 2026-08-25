# AGENTS.md

Instructions, rules hierarchy, and reference map for agents working in `MLOps` (the Zero→Hero workspace).

> **Learn every layer by building it.** One theme — content personalization — carried from first event to production-grade platform.

<critical>
At session start and before every task, check whether `AGENTS.local.md` exists at the repository root.
If present, read it FIRST and treat it as the highest-precedence instruction source — especially for
machine constraints (RAM budgets, service startup discipline, local tooling).
Where it conflicts with this file or `.agents/rules/`, `AGENTS.local.md` wins. It is developer-local
and must never be committed.
</critical>

---

## 1. Instruction Hierarchy & Reference Mapping

| Document | Scope & Purpose | Precedence |
|:---|:---|:---|
| [`AGENTS.local.md`](./AGENTS.local.md) | Machine-local constraints and preferences (gitignored). | Highest (developer machine overrides) |
| [`.computers/*.md`](./.computers/) | Machine facts per box — `MACBOOK.md` (authoring), `THINKBOOK.md` (deploy target), `WORKSTATION.md` (CloudThinker VM, out of scope). Durable facts as values, moving facts as commands (gitignored). Referenced everywhere instead of hardcoded specs. | Facts source (read alongside local overrides) |
| [`.agents/rules/*.md`](./.agents/rules/) | Strict operational rules for this codebase. | Mandatory rules (mapped below) |
| [`AGENTS.md`](./AGENTS.md) | Core agent philosophy, stack, behavior (this file). | Project-wide foundation |
| [`CONTEXT-MAP.md`](./CONTEXT-MAP.md) | Pipeline bounded contexts, language ownership, vocabulary. Root hub — the only context file at root. | Domain vocabulary & constraints |
| [`*/CONTEXT.md`](./CONTEXT-MAP.md) | Per-module deep dives, living beside each module's code under `platform/` once it exists (Tribal convention). | Module-level detail |
| [`.worklog/FOCUS.md`](./.worklog/FOCUS.md) | Current phase, active threads, handoff notes (gitignored). | Session state — read at start |
| [`docs/adr/`](./docs/adr/) | Architecture decision records with alternatives. | Binding unless superseded by a newer ADR |
| [`docs/agents/knowledge/`](./docs/agents/knowledge/) | Transferable knowledge notes (stack pins, bus contracts, streaming constraints); architectural decisions graduate into [`docs/adr/`](./docs/adr/) | Background knowledge & decisions |
| [`README.md`](./README.md) | Public-facing overview. | Presentation, not instructions |

### Rules Mapping (`.agents/rules/`)

- [`read-before-write.md`](./.agents/rules/read-before-write.md): search notes/docs/code before creating anything; reuse over reinvention.
- [`keep-docs-alive.md`](./.agents/rules/keep-docs-alive.md): docs evolve atomically with work — indexes, decision log, roadmap stay in lockstep.
- [`verify-before-done.md`](./.agents/rules/verify-before-done.md): claims come from execution — compile checks, `docker compose config`, generated artifacts regenerated.
- [`minimal-footprint.md`](./.agents/rules/minimal-footprint.md): touch only what the task requires; every changed line traces to the requirement.
- [`resource-budget.md`](./.agents/rules/resource-budget.md): RAM-constrained machine (`.computers/MACBOOK.md`) — never run the whole stack; one profile group at a time, measured.
- [`reference-clones-read-only.md`](./.agents/rules/reference-clones-read-only.md): `.repos/` clones are untouched upstream checkouts; learning goes to `.notes/`.
- [`generated-artifacts.md`](./.agents/rules/generated-artifacts.md): never hand-edit generated files (`metadata.json`, `docs/**/index.json`) — fix the generator or registry, then regenerate.

### Language Rules (`.agents/rules/`)

One umbrella per owned language ([ADR 0004](./docs/adr/0004-polyglot-language-per-concern.md)); each umbrella indexes its focused siblings:

- [`java-general.md`](./.agents/rules/java-general.md): Flink job + Kafka Streams service → streaming correctness, Maven build/testing.
- [`go-general.md`](./.agents/rules/go-general.md): gateway/BFF/simulators → concurrency & services, layout & testing.
- [`python-general.md`](./.agents/rules/python-general.md): Feast/Ray/MLflow/FastAPI plane → uv envs & quality, ML reproducibility.
- [`rust-general.md`](./.agents/rules/rust-general.md): retrieval hot path → types & errors, async & latency budgets, testing.

### Skills Mapping (`.agents/skills/`)

Skills are auto-discovered from `.agents/skills/`. Every skill is bound by the rules above and points to the docs it needs.

| Phase | Skill | Purpose |
|:---|:---|:---|
| Direction | `maintain-worklog`, `handoff` | Track durable project state (`.worklog/`) and compact context between sessions. |
| Design | `grilling`, `wait-what`, `domain-modeling`, `codebase-design` | Stress-test requirements, re-pitch complexity in domain terms, sharpen CONTEXT-MAP vocabulary and module seams before coding. |
| Study | `studying-mlops` | Protocol for walking a reference repo end-to-end and producing its topic note + index updates. |
| Implement | `implement`, `tdd` | Drive feature, bug-fix, and test work with incremental verification loops. |
| Review | `deslopify`, `codebase-review`, `improve-codebase-architecture` | Pre-PR diff slop removal, two-axis review against spec and standards, architectural friction scans. |
| Research | `experiment` | Run isolated benchmark/model experiments against baselines; record outcomes in `docs/agents/`. |
| Operate | `managing-mlops-services` | RAM-budget-aware lifecycle for service groups: preflight, start one group, health-check, capture actuals, teardown. |
| Git | `resolving-merge-conflicts` | Cleanly resolve in-progress merges or rebases. |

---

## 2. Project Overview

This workspace carries **Zero to Hero in MLOps** themed **content personalization** ([ADR 0001](./docs/adr/0001-content-personalization-theme.md)): user interactions → Debezium CDC → Kafka → stream processing → MinIO/Iceberg lakehouse → Feast features (offline Iceberg, online Redis) → Ray Train + MLflow → serving → frontend behind NGINX → observability → Superset analytics.

- Learning notes: `.notes/` (local-only, gitignored) — roadmap at [`.notes/00-roadmap.md`](./.notes/00-roadmap.md).
- Reference clones: `.repos/` (local-only, gitignored) — provenance in generated `.repos/metadata.json`.
- The build itself lands in `platform/` when Phase 1 starts; until then no runtime code exists.
- Phases 0–8 with checkboxes live in the roadmap; the honest Implemented-vs-Reserved snapshot lives in [`CONTEXT-MAP.md`](./CONTEXT-MAP.md).

## 3. Core Behavioral Principles

### Principle 1: Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State assumptions explicitly before implementing. If uncertain or facing ambiguities, ask.
- If multiple interpretations exist, present concrete options — do not choose silently.
- If a simpler approach exists, propose it. Push back when complexity is unwarranted.

### Principle 2: Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- Implement only what the task asks; avoid single-use abstractions and speculative configurability.
- *Ask:* "Would a senior engineer call this overcomplicated?" If yes, simplify.

### Principle 3: Surgical Changes
**Touch only what you must.**
- Do not improve adjacent code, comments, formatting, or rename existing symbols.
- Match existing patterns and style; clean up only your own unused imports/artifacts.
- *The Test:* every changed line traces directly to the task requirement.

### Principle 4: Goal-Driven Execution
**Define success criteria. Loop until verified.**
- Break tasks into `[step] → verify: [check]` milestones before executing.
- Bug fixes reproduce the failure first, then fix, then prove the test green.

### Principle 5: Prove It By Running
**Claims about behavior come from execution, not intuition.**
- Never guess what a command or service does — run it and observe.
- Resource claims (RAM, latency) get measured values recorded where the next session finds them.
- An experiment without recorded results did not happen.

## 4. Stack & Conventions

Polyglot by design — each concern owns the language that fits it ([ADR 0004](./docs/adr/0004-polyglot-language-per-concern.md)); versions are latest stable at adoption:

| Concern | Language/Runtime | Enters at |
|:---|:---|:---|
| Stream processing: Flink jobs, one Kafka Streams enrichment service | Java 25 (LTS) | Phase 1–2 |
| ML plane: Feast features, Ray Train/Tune, MLflow, FastAPI/Ray Serve internals | Python 3.14 | Phase 2 |
| Event gateway, app-facing BFF, simulators/load generators | Go 1.27 | Phase 1 (gateway), Phase 5 (BFF) |
| Retrieval/ranking hot path (Redis feature join + light scoring) | Rust 1.98 (edition 2024) | Phase 4 |
| Frontend: SvelteKit (Svelte 5), Bun toolchain on Node 24 LTS runtime, strict TypeScript | TypeScript (latest) | Phase 5 |
| Contracts between services | OpenAPI + Avro/JSON Schema | always |
| Warehouse/lakehouse transforms | SQL | Phase 1 |

- Infra services (Kafka, Debezium, MinIO, Redis, Elasticsearch, SigNoz, Grafana, Prometheus, Superset) are config-only — no code, compose-managed ([ADR 0003](./docs/adr/0003-ram-budgeted-local-infrastructure.md)).
- Exact infra versions are pinned per-phase in the compose files, never from memory.
- Markdown: one physical line per paragraph/bullet.

## 5. Commands & Verification

```bash
python3 scripts/gen_repos_metadata.py            # regenerate .repos/metadata.json after clone changes
python3 scripts/gen_repos_metadata.py --check    # exit 1 if output would change (drift check)
docker stats --no-stream                         # check live container memory before/after any compose up
```

### Required pre-completion verification

Before declaring any task complete:
1. Touched code passes its language gate: Python → `ruff check` + `ty`/`basedpyright`; Go → `go vet`/`gofmt`; Rust → clippy/fmt; Java → Maven package — plus `python3 -m py_compile <files>` for quick syntax sanity, and execution wherever behavior matters (gates apply as each phase's toolchain/config lands).
2. `.repos/` changed ⇒ metadata regenerated and committed delta includes it.
3. Docs touched code or facts ⇒ related index/table rows updated atomically (`keep-docs-alive`).
4. Compose changes (future) ⇒ `docker compose ... config -q` validates, and `resource-budget` honored.

## 6. Directory Contract

| Path | Purpose | Git |
|:---|:---|:---|
| `AGENTS.md`, `CONTEXT-MAP.md`, `README.md` | Root context layer (hub stays single at root) | tracked |
| `AGENTS.local.md` | Machine rules (this Mac) — facts live in `.computers/MACBOOK.md` | ignored |
| `.computers/` | Per-box machine facts: MACBOOK (authoring), THINKBOOK (deploy target), WORKSTATION (out of scope) | ignored |
| `.agents/rules/`, `.agents/skills/` | Operational rules + phase skills | tracked |
| `docs/adr/`, `docs/agents/`, `docs/README.md` | Decision records + research log | tracked |
| `platform/**/CONTEXT.md` | Per-module context docs, beside their code (created with modules) | tracked once created |
| `scripts/` | Generators + curated registries (tracked); outputs may be local | tracked |
| `.notes/` | Learning notes (roadmap, topic walkthroughs) | ignored |
| `.repos/` | Reference clones + generated `metadata.json` | ignored |
| `.worklog/` | Session state (`FOCUS.md`) | ignored |
