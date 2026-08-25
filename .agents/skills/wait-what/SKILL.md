---
name: wait-what
description: Re-pitch an unclear or overly complex explanation in clear, simple technical language grounded in the pipeline's domain vocabulary.
---

# Wait What — Technical Re-Pitch

Reset and re-explain complex concepts, decisions, or pipeline states in clear, concise technical English.

## Re-Pitch Guidelines

1. **Context Baseline**: the high-level goal in 1-2 plain sentences.
2. **Domain Grounding**: use exact terms from [`CONTEXT-MAP.md`](../../../CONTEXT-MAP.md) — *interaction event*, *candidate retrieval*, *ranking*, *feature vector*, *online/offline store*, *point-in-time correctness*, *profile group*. Not "the recs stuff".
3. **Strip Jargon**: replace meta-commentary with direct causal statements — "Doing X because Y produces Z".
4. **Concrete Example**: a small snippet, command run, or data table illustrating the point:

```
GET /v1/recommendations?user_id=42
→ retrieval(rust): 500 candidates from Redis+ES   [p99 budget 40ms]
→ ranking(fastapi): score via feature vectors     [model v7 @ MLflow]
→ bff(go): top-20 + impression logging → Kafka
```
