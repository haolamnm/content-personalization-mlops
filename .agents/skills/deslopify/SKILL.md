---
name: deslopify
description: Remove AI-generated slop from a branch diff — narrating comments, needless defensive checks, unwrap/clone spam, over-nesting, Fowler smells — and match the surrounding language's style. Use before opening a PR or when asked to "deslopify".
---

# Remove AI code slop

Check the diff against the default branch and remove AI-generated slop introduced in the branch. Run after `implement`/`tdd` and before `codebase-review`; `CONTEXT-MAP.md` and `.agents/rules/` define what "ours" means when matching surrounding style.

## Scope

In-branch cleanup only. Findings needing cross-file restructuring (Feature Envy, Data Clumps, Shotgun Surgery, Divergent Change) get flagged and handed to `codebase-review`, not restructured here.

## Focus Areas

- **Narrating comments**: "increment counter" slop. Keep concise *why* comments; drop what restates the code.
- **Defensive noise**: nil/empty checks and error branches on paths that cannot fire. Fix with typed errors at the seam instead (`rust-types-and-error-handling`, Go's wrapped errors, Java's sealed result types).
- **Clone/copy spam**: `.clone()` to silence the borrow checker, needless `.to_vec()`/`list(...)` copies where borrows/views work.
- **Casts that bypass types**: `as`-narrowing, `int(x)` around already-typed values, stringly flags that want an enum or newtype.
- **Hardcoded literals** that deserve named constants (with a *why* comment).
- **Deep nesting** that collapses with early returns / `?` / guard clauses.

## Fowler Smell Checklist

Judgement calls, not hard violations: Mysterious Name, Duplicated Code, Primitive Obsession, Speculative Generality, Message Chains, Middle Man. A documented rule in `AGENTS.md`/`.agents/rules/` overrides this baseline (e.g. `minimal-footprint` prefers smallest change). Skip anything the language gate already enforces (clippy, go vet, ruff).

## Guardrails

- Behavior unchanged unless fixing a clear bug; verify with the touched language's gate (`verify-before-done`) after cleanup.
- Minimal, focused edits; keep the final summary to 1-3 sentences.
