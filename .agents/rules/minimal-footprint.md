---
description: Touch only what the task requires; every changed line traces to the requirement
globs: []
alwaysApply: true
---

# Rule: Minimal Footprint

Change only what the task needs.

## Constraints

- **Traceability test**: every changed line maps to the stated requirement; incidental cleanups are named in the report or not made.
- **No drive-by improvements**: adjacent code, comments, formatting, and naming stay untouched unless the task requires them.
- **Match existing patterns**: new code mimics the style of its bounded context; new services follow ADR language ownership without improvising.
- **Scope guard on docs**: do not restructure indexes/maps while fixing a fact — atomic does not mean expansive.
