package gateway

import (
	"strings"
	"testing"
)

func TestEventValidate(t *testing.T) {
	tests := []struct {
		name    string
		event   Event
		wantErr string // empty means expect success
	}{
		{
			name:  "valid click",
			event: Event{UserID: "u_42", ItemID: "item_7", EventType: EventClick},
		},
		{
			name:  "valid impression",
			event: Event{UserID: "u1", ItemID: "i1", EventType: EventImpression},
		},
		{
			name:    "missing user_id",
			event:   Event{ItemID: "item_7", EventType: EventClick},
			wantErr: "user_id is required",
		},
		{
			name:    "blank item_id",
			event:   Event{UserID: "u_42", ItemID: "   ", EventType: EventClick},
			wantErr: "item_id is required",
		},
		{
			name:    "unknown event_type",
			event:   Event{UserID: "u_42", ItemID: "item_7", EventType: "hover"},
			wantErr: "event_type must be one of",
		},
		{
			name:    "empty event_type",
			event:   Event{UserID: "u_42", ItemID: "item_7"},
			wantErr: "event_type must be one of",
		},
		{
			name:    "multiple problems reported together",
			event:   Event{EventType: "hover"},
			wantErr: "user_id is required; item_id is required; event_type must be one of",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.event.Validate()
			if tt.wantErr == "" {
				if err != nil {
					t.Fatalf("want success, got %v", err)
				}
				return
			}
			if err == nil || !strings.Contains(err.Error(), tt.wantErr) {
				t.Fatalf("want error containing %q, got %v", tt.wantErr, err)
			}
		})
	}
}
