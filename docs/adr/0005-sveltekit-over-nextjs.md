---
title: "ADR 0005 — SvelteKit over Next.js for the App"
id: adr-0005
date: 2026-08-25
type: adr
status: accepted
tags: [frontend, sveltekit, svelte5, nextjs]
related:
  - ./0004-polyglot-language-per-concern.md
---

# ADR 0005 — SvelteKit over Next.js for the App

## Status

Accepted (2026-08-25). Revisit only if a concrete need (e.g., React-team portfolio signaling) outweighs the bundle/runtime cost recorded below.

## Context

The app context needs a personalized-feed UI emitting interaction events, served behind NGINX. The requirement is optimization, not familiarity: minimal shipped JS, no framework bloat, SSR-capable, TypeScript-first.

## Decision

**SvelteKit (Svelte 5 runes) on Node 24 LTS, strict TypeScript.** Svelte is a compiler: components compile away to near-vanilla DOM operations, so baseline hydration cost is dramatically smaller than virtual-DOM runtimes — the right shape for an event-emitting feed that must stay light on low-end devices.

## Alternatives Considered

1. **Next.js / React**: rejected as default — excellent ecosystem, but ships a heavier runtime (React reconciler + RSC/server-action machinery) that buys nothing for this app; also the "default" choice teaches the least about FE compilation models.
2. **SolidStart (SolidJS)**: close second — fine-grained reactivity, tiny bundles; lost on smaller ecosystem and fewer learning resources than Svelte 5.
3. **Astro islands**: rejected — optimized for content sites with sparse interactivity; a recs feed is app-shell interactive throughout.
4. **Qwik**: rejected for now — resumability is promising but the ecosystem/maturity risk is real for a project meant to finish.
5. **Plain Vite + React/Vue SPA**: rejected — gives up SSR/routing conventions without gaining anything over SvelteKit.
6. **HTMX + Go templates**: honestly tempting for leanness, rejected — abandons rich client-side interactions (optimistic UI, event batching) that the personalization loop wants to demo.

## Consequences

- FE codebase stays small enough to audit by reading; bundle-size regressions become visible in review, not hidden under framework weight.
- React-specific portfolio signals are traded away deliberately; the compensating signal is measured performance (Lighthouse/bundle budgets recorded in Phase 5).
- Svelte 5 runes are new-ish API surface; pin exact versions in `platform/app/package.json` when created.
- JS toolchain locked to **Bun** (installs/scripts) with **pnpm as fallback**; npm excluded — install speed and disk weight without offsetting benefit. The server runtime stays Node 24 LTS via SvelteKit's adapter-node (most battle-tested deploy path); a Bun-runtime experiment may follow later without changing lockfile discipline.
