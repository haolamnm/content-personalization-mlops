---
title: "Content Catalog Context"
id: content-catalog-context
date: 2026-08-27
type: context
status: active
tags: [go, mongodb, catalog, cdc]
related:
  - ../../../../CONTEXT-MAP.md
  - ../../../../docs/agents/architecture/domain-contracts.md
  - ../../../../.agents/rules/go-general.md
---

# Content Catalog (`platform/services/content-catalog/`)

The Content Catalog owns document-shaped metadata for recommendable content. MongoDB is its system of record; the catalog's canonical `ContentItem.ID` is the same identifier carried as an interaction event's `item_id`.

## Canonical vocabulary

- **Content item**: a catalog document that may be recommended; avoid using “interaction” or “event” for the document.
- **Content kind**: article, video, or product; avoid using `event_type`, which belongs to interaction events.
- **Publication status**: active or archived; only active items belong in the candidate source.
- **Catalog reader**: the `Reader` port used by future retrieval/BFF code; avoid direct MongoDB calls outside the repository adapter.

## Document contract

`content_items` uses a string `_id` that is stable across MongoDB, interaction `item_id`, CDC keys, and future candidate indexes. Each document carries `kind`, `title`, `description`, `categories`, `tags`, `status`, `published_at`, `created_at`, and `updated_at`. Timestamps are UTC and the repository rejects invalid kind/status values and an `updated_at` earlier than `created_at`.

## Boundaries

- `catalog.Reader` owns `GetByID` and deterministic active listing for downstream consumers.
- `catalog.Writer` owns idempotent fixture/upsert writes; there is no public mutation API yet.
- `MongoRepository` is the only persistence adapter and maps missing IDs to `ErrNotFound`.
- The MongoDB Debezium connector publishes changes from `mlops_catalog.content_items` to `mlops_mongodb.mlops_catalog.content_items`; CDC records are transport facts, not catalog documents.

## Verification

Unit tests prove document invariants and stable seed contents. The integration test seeds a dedicated database/collection and reads by ID plus active listing against a real MongoDB. The k3s gate additionally proves a catalog write reaches the MongoDB CDC topic.
