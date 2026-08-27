// Package catalog owns the content-item contract and its MongoDB repository boundary.
package catalog

import (
	"fmt"
	"strings"
	"time"
)

// ContentKind describes the catalog media shape, not the user's interaction with it.
type ContentKind string

const (
	KindArticle ContentKind = "article"
	KindVideo   ContentKind = "video"
	KindProduct ContentKind = "product"
)

// PublicationStatus describes whether a content item can be returned for retrieval.
type PublicationStatus string

const (
	StatusActive   PublicationStatus = "active"
	StatusArchived PublicationStatus = "archived"
)

// ContentItem is the canonical MongoDB document for a recommendable catalog item.
// Its ID is also the item_id carried by interaction events.
type ContentItem struct {
	ID          string            `bson:"_id" json:"id"`
	Kind        ContentKind       `bson:"kind" json:"kind"`
	Title       string            `bson:"title" json:"title"`
	Description string            `bson:"description" json:"description"`
	Categories  []string          `bson:"categories" json:"categories"`
	Tags        []string          `bson:"tags" json:"tags"`
	Status      PublicationStatus `bson:"status" json:"status"`
	PublishedAt time.Time         `bson:"published_at" json:"published_at"`
	CreatedAt   time.Time         `bson:"created_at" json:"created_at"`
	UpdatedAt   time.Time         `bson:"updated_at" json:"updated_at"`
}

// Validate checks the document invariants at the repository boundary.
func (item ContentItem) Validate() error {
	var problems []string
	if strings.TrimSpace(item.ID) == "" {
		problems = append(problems, "id is required")
	} else if item.ID != strings.TrimSpace(item.ID) {
		problems = append(problems, "id must not have surrounding whitespace")
	}
	if item.Kind != KindArticle && item.Kind != KindVideo && item.Kind != KindProduct {
		problems = append(problems, "kind must be article, video, or product")
	}
	if strings.TrimSpace(item.Title) == "" {
		problems = append(problems, "title is required")
	}
	if item.Status != StatusActive && item.Status != StatusArchived {
		problems = append(problems, "status must be active or archived")
	}
	if item.CreatedAt.IsZero() {
		problems = append(problems, "created_at is required")
	}
	if item.UpdatedAt.IsZero() {
		problems = append(problems, "updated_at is required")
	}
	if !item.CreatedAt.IsZero() && !item.UpdatedAt.IsZero() && item.UpdatedAt.Before(item.CreatedAt) {
		problems = append(problems, "updated_at must not precede created_at")
	}
	if len(problems) > 0 {
		return fmt.Errorf("invalid content item: %s", strings.Join(problems, "; "))
	}
	return nil
}
