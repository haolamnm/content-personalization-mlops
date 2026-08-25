---
description: Types at boundaries and error handling for the Rust retrieval service — newtypes, enums, thiserror/anyhow split
globs: ["**/*.rs"]
alwaysApply: false
---

# Rule: Rust Types & Error Handling

## Constraints

- **Newtype external identifiers**: user/item/session IDs are distinct newtypes, never raw `u64`/`String` crossing function boundaries — mixing them up must not compile.
- **Enums over booleans**: request states, cache outcomes, and feature-vector completeness are enums; `bool` parameters that select behavior are banned.
- **`thiserror` at the library seam, `anyhow` only in `main`**: the service core returns typed errors; stringly-typed errors and `.unwrap()` outside tests are banned.
- **Errors carry enough to act**: each variant states what failed and what the caller should do next (retry, fallback to warm candidates, degrade to popular items) — silent degradation is banned.
- Parse, don't validate twice: convert wire types into domain types once at the edge; downstream code sees only valid domain values.
