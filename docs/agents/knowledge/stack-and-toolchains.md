---
title: "Stack & Toolchains"
id: agents-knowledge-stack-toolchains
date: 2026-08-25
type: knowledge
status: active
tags: [toolchain, java, go, python, rust, typescript]
related:
  - ../../adr/0004-polyglot-language-per-concern.md
  - ../../adr/0005-sveltekit-over-nextjs.md
  - ../../../.agents/rules/python-envs-and-quality.md
---

# Stack & Toolchains

Operative toolchain facts behind [ADR 0004](../../adr/0004-polyglot-language-per-concern.md) / [ADR 0005](../../adr/0005-sveltekit-over-nextjs.md). Versions live here and in `.computers/` fact files — never from memory.

## Locked choices

- **Java 25** (Flink/Kafka Streams) via keg-only `openjdk@25`; export `JAVA_HOME=/opt/homebrew/opt/openjdk@25/libexec/openjdk.jdk/Contents/Home` per-project (repo `.envrc` convention).
- **Go 1.27**, GOPATH at XDG `~/.local/share/go`, GOBIN → `~/.local/bin`.
- **Python 3.14**; quality = **ruff** (lint+format) + **ty**/**basedpyright** (types) — no mypy, no black. The three are dev deps of the root `pyproject.toml` (uv-managed, `.venv` gitignored); run gates as `uv run ruff check/format`, `uv run ty check scripts`, `uv run basedpyright scripts` — never global tool installs.
- **Rust 1.98** for the retrieval hot path.
- **Node 24 LTS** is the server runtime via volta shims (`~/.local/share/volta`); brew node stays installed but shadowed. **Bun** primary JS toolchain, **pnpm** fallback, npm banned (amends ADR 0005).
- **Maven over Gradle**: no persistent daemon RAM (ADR 0003 constraint); Flink/Kafka docs are Maven-first.

## Practice

- Agent search is `rg`, never grep.
- Snapshot dependencies or `-U` force-updates need a note in the relevant knowledge doc before use.
- Toolchain installs/changes get recorded in `.computers/MACBOOK.md`, not in prose.
