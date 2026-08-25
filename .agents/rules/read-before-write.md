---
description: Search notes, docs, and existing code before creating anything; reuse over reinvention
globs: []
alwaysApply: true
---

# Rule: Read Before Write

Read what exists before creating anything new.

## Constraints

- **Search first**: check `.notes/topics/`, `docs/`, and `platform/` for prior art on a topic or primitive before writing a new note, script, or service.
- **Reuse over reinvention**: if `scripts/` already generates an artifact, extend it; do not hand-roll a parallel path.
- **Understand the seam**: identify which bounded context (CONTEXT-MAP §1) owns the code you are touching and who consumes it before changing contracts.
- **Docs count as callers**: contradicting CONTEXT-MAP.md or an ADR in code means updating those docs is part of the task, not an afterthought.
