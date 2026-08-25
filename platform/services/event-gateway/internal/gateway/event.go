// Package gateway holds the interaction-event domain type and its validation.
package gateway

import (
	"fmt"
	"strings"
	"time"
)

// EventType is the set of interaction events the platform recognizes.
type EventType string

const (
	EventImpression EventType = "impression"
	EventClick      EventType = "click"
	EventDwell      EventType = "dwell"
	EventLike       EventType = "like"
	EventShare      EventType = "share"
)

var allowed = map[EventType]bool{
	EventImpression: true,
	EventClick:      true,
	EventDwell:      true,
	EventLike:       true,
	EventShare:      true,
}

// Event is one user interaction with a content item — the unit of ingestion.
type Event struct {
	UserID    string    `json:"user_id"`
	ItemID    string    `json:"item_id"`
	EventType EventType `json:"event_type"`
	CreatedAt time.Time `json:"created_at"`
}

// Validate checks required fields and the event vocabulary.
func (e Event) Validate() error {
	var problems []string
	if strings.TrimSpace(e.UserID) == "" {
		problems = append(problems, "user_id is required")
	}
	if strings.TrimSpace(e.ItemID) == "" {
		problems = append(problems, "item_id is required")
	}
	if !allowed[e.EventType] {
		problems = append(problems, "event_type must be one of: impression, click, dwell, like, share")
	}
	if len(problems) > 0 {
		return fmt.Errorf("invalid event: %s", strings.Join(problems, "; "))
	}
	return nil
}
