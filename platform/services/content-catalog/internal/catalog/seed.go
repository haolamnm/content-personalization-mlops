package catalog

import (
	"context"
	_ "embed"
	"encoding/json"
	"fmt"
)

//go:embed seed/catalog.json
var seedData []byte

// Seed writes the deterministic catalog fixture through the writer boundary.
func Seed(ctx context.Context, writer Writer) error {
	var items []ContentItem
	if err := json.Unmarshal(seedData, &items); err != nil {
		return fmt.Errorf("decode catalog seed: %w", err)
	}
	for _, item := range items {
		if err := writer.Upsert(ctx, item); err != nil {
			return fmt.Errorf("seed %q: %w", item.ID, err)
		}
	}
	return nil
}
