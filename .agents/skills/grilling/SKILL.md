---
name: grilling
description: Interactively grill and stress-test architecture plans, requirements, or design decisions with structured questioning rounds.
---

# Grilling & Architectural Interview

Interview and stress-test plans, decisions, or ambiguous requirements until full alignment is reached.

## The Decision Frontier Protocol

Map all decisions as a **dependency tree**:
- **The Frontier**: open decisions whose prerequisites are already settled.
- **Round-by-Round**: ask all frontier questions in one structured round; never ask questions that depend on unresolved branches.
- **Facts vs Decisions**: look up code facts, existing decision-log rows ([`docs/agents/decision-log.md`](../../../docs/agents/decision-log.md)), and ADRs autonomously; only ask the user for genuine choices.

## Question Formatting

```markdown
**Q1: <Decision Title>**
<Context explaining the trade-off and options>
- Option A: ...
- Option B: ...

**Recommendation**: <Concrete recommended option and reason>
```

Check the ADRs and decision log first — a question already answered there is not a question, it's a citation. Reversing an ADR requires a superseding ADR, not a chat agreement.

## Session Completion

A grilling session concludes when the frontier is fully resolved and all assumptions are explicitly validated. Record new resolutions as dated decision-log rows.
