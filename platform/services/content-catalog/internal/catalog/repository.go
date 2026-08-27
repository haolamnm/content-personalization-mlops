package catalog

import (
	"context"
	"errors"
)

// ErrNotFound is returned when an item ID has no catalog document.
var ErrNotFound = errors.New("content item not found")

// Reader is the read seam consumed by future retrieval and BFF code.
type Reader interface {
	GetByID(ctx context.Context, id string) (ContentItem, error)
	ListActive(ctx context.Context, limit int) ([]ContentItem, error)
}

// Writer is intentionally narrow: only catalog seeding currently writes documents.
type Writer interface {
	Upsert(ctx context.Context, item ContentItem) error
}

// Repository is the Mongo-backed content catalog boundary.
type Repository interface {
	Reader
	Writer
}
