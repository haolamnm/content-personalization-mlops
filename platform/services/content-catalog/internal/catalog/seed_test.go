package catalog

import (
	"context"
	"testing"
)

type recordingWriter struct {
	items []ContentItem
}

func (w *recordingWriter) Upsert(_ context.Context, item ContentItem) error {
	w.items = append(w.items, item)
	return nil
}

func TestSeedWritesStableCatalog(t *testing.T) {
	writer := &recordingWriter{}

	if err := Seed(context.Background(), writer); err != nil {
		t.Fatalf("Seed() error = %v", err)
	}

	if len(writer.items) != 3 {
		t.Fatalf("seed item count = %d, want 3", len(writer.items))
	}
	if got := writer.items[0].ID; got != "article-001" {
		t.Fatalf("first seed id = %q, want article-001", got)
	}
	if got := writer.items[1].ID; got != "video-001" {
		t.Fatalf("second seed id = %q, want video-001", got)
	}
	if got := writer.items[2].Status; got != StatusArchived {
		t.Fatalf("third seed status = %q, want archived", got)
	}
}
