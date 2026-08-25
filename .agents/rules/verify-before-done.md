---
description: Claims come from execution — compile checks, compose config validation, generators re-run
globs: []
alwaysApply: true
---

# Rule: Verify Before Done

A task is done when it is proven to run, not when it looks finished.

## Constraints

- **Touched code executes or compiles**: Python `python3 -m py_compile <files>` minimum, executed where behavior matters; Go/Java/Rust/TS gates arrive with each phase's toolchain and then become mandatory.
- **Compose validates**: any compose file change passes `docker compose -f <file> config -q` before up.
- **Generated artifacts regenerate**: after `.repos/` or registry changes run `python3 scripts/gen_repos_metadata.py --check`; a diff means you edited output by hand somewhere.
- **Resource claims measured** ([Principle 5](../../AGENTS.md)): RAM/latency numbers come from `docker stats`/timings recorded where the next session finds them.
- **No green-by-assumption**: if a check could not run (tooling missing), say so explicitly instead of claiming success.
