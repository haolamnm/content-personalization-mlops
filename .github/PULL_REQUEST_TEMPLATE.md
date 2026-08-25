# What & Why

<!-- One paragraph: what this PR changes and why it exists. Link the driving ADR, roadmap phase, or issue. -->

## Changes

-

## Verification

Per [verify-before-done](../.agents/rules/verify-before-done.md) — claims come from execution, not intention.

- [ ] Touched code passes its language gate (`ruff` + `ty`/basedpyright · `go vet`/gofmt · clippy/fmt · `mvn package`; n/a for config-only changes)
- [ ] Behavior claims backed by a real run — note command + observed result below
- [ ] Compose touched ⇒ `docker compose ... config -q` green; resource-budget rules ([ADR 0003](../docs/adr/0003-ram-budgeted-local-infrastructure.md)) honored
- [ ] `.repos/` changed ⇒ `metadata.json` regenerated (`python3 scripts/gen_repos_metadata.py --check`)

## Docs alive

Per [keep-docs-alive](../.agents/rules/keep-docs-alive.md) — docs move atomically with work.

- [ ] CONTEXT-MAP §4 (Implemented vs Reserved) matches post-merge reality
- [ ] Module `CONTEXT.md` updated if `platform/**` is touched
- [ ] Decision-log rows appended for every decision made here
- [ ] Indexes drift-free: `python3 scripts/gen_docs_metadata.py --check`

## Notes for reviewers

<!-- Measured numbers, deferred items, open questions. -->
