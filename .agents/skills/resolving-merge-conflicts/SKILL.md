---
name: resolving-merge-conflicts
description: Resolve in-progress git merge or rebase conflicts cleanly. Use when handling merge conflicts, rebasing branches, or cherry-picking commits.
---

# Resolving Merge Conflicts

Resolve conflicts safely by understanding the original intent of all changes and validating with automated checks.

## Protocol

1. **Assess Conflict Scope**:
   ```bash
   git status
   git diff --name-only --diff-filter=U
   ```
2. **Inspect Primary Sources & Intent**:
   - `git log -n 5 <branch>` on both sides; understand *why* each changed the conflicting lines.
3. **Resolve Each Conflict Hunk**:
   - Preserve the intent of both changes where possible.
   - Logically incompatible changes: prioritize the target branch's stated goal and surface the trade-off explicitly.
   - **Never invent unrequested behavior** during resolution.
   - Never `git merge --abort` unless explicitly directed.
4. **Run Automated Verification** — full gate for every touched language (`.agents/rules/verify-before-done.md`):
   ```bash
   # Python      ruff check && ty check && basedpyright
   # Go          go vet ./... && gofmt -l .
   # Rust        cargo clippy --all-targets && cargo fmt --check
   # Java        mvn -q package
   ```
5. **Finalize**:
   - Stage resolved files explicitly (`git add <file>`).
   - Conclude (`git commit` or `git rebase --continue`).
