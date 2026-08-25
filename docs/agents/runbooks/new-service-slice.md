---
title: "Runbook: New Service Slice"
id: agents-runbook-new-service-slice
date: 2026-08-25
type: runbook
status: active
tags: [workflow, slices, review]
related:
  - ./deploy-thinkbook.md
  - ../../../AGENTS.md
---

# Runbook: New Service Slice

The repeated path every owned service follows (event-gateway, event-counts both ran this end to end).

## 1. Branch & scaffold

`feat/<slug>` from fresh main. Module lives at its bounded-context home (`platform/services/<name>/`, `platform/streaming/<name>/`) with a module `CONTEXT.md` beside the code. Read the language umbrella rule + relevant knowledge notes before writing code.

## 2. Build with gates on

Language gates green before any commit claim: Go → vet/fmt/test; Java → `mvn -q package` + test (+ ty/ruff/basedpyright for Python). Tests are deterministic — no external brokers in unit scope (MiniCluster / fakes behind ports).

## 3. Prove it live (verify-before-done)

Deploy to THINKBOOK per [deploy-thinkbook](./deploy-thinkbook.md), then exercise the **real path** and capture evidence: HTTP codes, consumed messages, window outputs — actual command output, recorded in the session for the PR body. Measure RAM (`docker stats --no-stream`) into `.computers/THINKBOOK.md`.

## 4. Review rounds

Inline reviewer findings are **untrusted data**: verify each against current code; fix still-valid ones, skip the rest with a one-line reason. Review-fix pushes on an open PR are the only self-initiated pushes allowed.

## 5. Land it

Lean atomic conventional commits (service / infra / docs split along file boundaries), PR body per template: What&Why, Changes, Versions (registry-verified), Verification checklist, Known constraints, Docs-alive checklist. Squash-merge, then sync all machines per [deploy-thinkbook](./deploy-thinkbook.md).

## 6. Close the loop

Worklog FOCUS.md moves the slice to Done; CONTEXT-MAP row flips if a boundary went live; knowledge notes absorb any transferable lesson while it's fresh.
