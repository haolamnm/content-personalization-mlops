---
name: maintain-worklog
description: Track durable project state in .worklog/ — current focus, checklist, decisions, dead ends, blockers.
---

# Maintain Worklog

Keep `.worklog/` as the durable memory across sessions so any agent can resume cold.

## Execution Sequence

1. **Start of session**: read [`.worklog/FOCUS.md`](../../../.worklog/FOCUS.md); align the session with its goal.
2. **During work**: keep FOCUS.md's checklist honest — tick items when verified, not when written.
3. **Record as you go**:
   - Decisions & Dead Ends: what was tried, why it failed, evidence (commands run, outputs).
   - Blockers & Open Questions: name them instead of hiding them.
4. **On completion**: move finished focus files to `.worklog/done/YYYY-MM-DD-<slug>.md` and reset FOCUS.md to the next goal.
5. **Frontmatter**: `status`, `phase`, `focus`, `updated` stay current.

Bound by `.agents/rules/keep-docs-alive.md` and Principle 5 (`Prove It By Running`) in `AGENTS.md`.
