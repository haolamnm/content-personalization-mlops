# Content Catalog

The content catalog owns canonical metadata for recommendable content items. MongoDB is the source of truth; interaction events carry only the same item ID and never copy catalog metadata into the event contract.

## Local verification

Run the unit suite and static gates from the repository root:

```bash
make catalog-test
make catalog-lint
```

The deterministic seed command writes the embedded fixture through the repository boundary. Set `MONGODB_URI` in the caller environment with `replicaSet=rs0` and any required credentials, plus `MONGODB_DATABASE` and `MONGODB_COLLECTION`, to target a k3s MongoDB instance:

```bash
MONGODB_URI="${MONGODB_URI:?set MONGODB_URI with replicaSet=rs0}" MONGODB_DATABASE=mlops_catalog MONGODB_COLLECTION=content_items go -C platform/services/content-catalog run ./cmd/catalog-seed
```

The integration read proof is opt-in and skips without a URI:

```bash
MONGODB_URI="${MONGODB_URI:?set MONGODB_URI with replicaSet=rs0}" go -C platform/services/content-catalog test -tags integration ./internal/catalog
```

## Boundary

`catalog.Reader` is the read seam for future retrieval and BFF code. `catalog.Writer` is intentionally limited to idempotent seed/upsert work until a product-owned mutation API exists. `MongoRepository` is the only implementation that touches MongoDB.
