---
title: "Runbook: Deploy to THINKBOOK"
id: agents-runbook-deploy-thinkbook
date: 2026-08-25
type: runbook
status: active
tags: [thinkbook, deploy, ssh]
related:
  - ../../adr/0006-thinkbook-remote-deployment-target.md
  - ../../../.computers/THINKBOOK.md
---

# Runbook: Deploy to THINKBOOK

Transport is Tailscale (`ssh thinkbook` alias); the ct-style ControlMaster keeps one multiplexed connection alive — plain `ssh thinkbook 'true'` should return in ~0.2s. If wedged: `ssh -O check thinkbook` / re-establish.

## Standard sync (fast-forward case)

```bash
git push thinkbook main          # deploy trigger (receive.denyCurrentBranch=updateInstead)
ssh thinkbook 'git -C ~/Workspaces/MLOps log --oneline -1'   # verify head moved
```

## After a squash-merge on GitHub (history diverged)

The push gets rejected (`working directory has unstaged changes` or non-FF). The worktree is disposable; `.env` and `~/.local/share/mlops/` are untracked:

```bash
ssh thinkbook 'bash -c "cd ~/Workspaces/MLOps && git fetch origin && git checkout -f main && git reset --hard origin/main"'
git push thinkbook main
```

This also cleans stray experiment files left by scp mishaps — audit with `git status --short` if it refuses again.

## Verify a slice after deploy

1. Group up: `make <group>-up` (data-guard whitelists sanctioned groups only)
2. Health: service-specific target (`gateway-health`) or `docker ps` badge
3. Functional probe through the real path (e.g. gateway POST → consumer read), never just port-open checks

## Runtime artifacts layout

Built jars/binaries → `~/.local/share/mlops/`; secrets in untracked `.env`. Nothing top-level dot-dir beyond XDG standards.
