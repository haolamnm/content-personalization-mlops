package catalog

import (
	"strings"
	"testing"
	"time"
)

func TestContentItemValidate(t *testing.T) {
	valid := ContentItem{
		ID:          "article-001",
		Kind:        KindArticle,
		Title:       "A useful article",
		Description: "A deterministic catalog fixture.",
		Categories:  []string{"engineering"},
		Tags:        []string{"mlops"},
		Status:      StatusActive,
		PublishedAt: time.Date(2026, time.January, 1, 0, 0, 0, 0, time.UTC),
		CreatedAt:   time.Date(2025, time.December, 1, 0, 0, 0, 0, time.UTC),
		UpdatedAt:   time.Date(2026, time.January, 1, 0, 0, 0, 0, time.UTC),
	}

	tests := []struct {
		name    string
		item    ContentItem
		wantErr string
	}{
		{name: "valid item", item: valid},
		{name: "missing id", item: func() ContentItem { item := valid; item.ID = " "; return item }(), wantErr: "id is required"},
		{name: "padded id", item: func() ContentItem { item := valid; item.ID = " article-001 "; return item }(), wantErr: "id must not have surrounding whitespace"},
		{name: "unknown kind", item: func() ContentItem { item := valid; item.Kind = "podcast"; return item }(), wantErr: "kind must be"},
		{name: "missing title", item: func() ContentItem { item := valid; item.Title = ""; return item }(), wantErr: "title is required"},
		{name: "unknown status", item: func() ContentItem { item := valid; item.Status = "draft"; return item }(), wantErr: "status must be"},
		{name: "updated before created", item: func() ContentItem { item := valid; item.UpdatedAt = item.CreatedAt.Add(-time.Second); return item }(), wantErr: "updated_at must not precede created_at"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.item.Validate()
			if tt.wantErr == "" {
				if err != nil {
					t.Fatalf("Validate() error = %v", err)
				}
				return
			}
			if err == nil || !strings.Contains(err.Error(), tt.wantErr) {
				t.Fatalf("Validate() error = %v, want substring %q", err, tt.wantErr)
			}
		})
	}
}
