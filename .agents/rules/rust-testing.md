---
description: Testing strategy for the Rust retrieval service — deterministic tests, property tests for scoring, bench gates
globs: ["**/*.rs"]
alwaysApply: false
---

# Rule: Rust Testing

## Constraints

- **Determinism**: tests control time (no wall-clock sleeps) and seed all randomness; a flaky test is a bug, not a retry.
- **Property tests for scoring/ranking logic** (`proptest`): score ordering invariants hold for arbitrary feature vectors — example-based tests alone don't cover the input space.
- **Contract fixtures**: Redis/ES response shapes are captured as fixture data so the join layer tests offline; live-service tests are integration-gated and never run inside the RAM budget rules ([`resource-budget`](./resource-budget.md)).
- **Benches are gates, not decoration**: `criterion` benches exist for every function on the request path; CI-less for now means the numbers land in `.computers/MACBOOK.md` §5 by hand ([`verify-before-done`](verify-before-done.md)).
- Bug fixes reproduce first: failing test → fix → green, in the same change.
