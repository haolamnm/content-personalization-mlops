package gateway

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"log/slog"
)

type fakeProducer struct {
	calls int
	keys  []string
	last  string
	err   error
}

func (f *fakeProducer) Produce(userID string, value []byte) error {
	f.calls++
	f.keys = append(f.keys, userID)
	f.last = string(value)
	return f.err
}

func post(s *Server, body string) *httptest.ResponseRecorder {
	req := httptest.NewRequest(http.MethodPost, "/events", strings.NewReader(body))
	rec := httptest.NewRecorder()
	s.Handler().ServeHTTP(rec, req)
	return rec
}

func TestHandleEvent(t *testing.T) {
	validBody := `{"user_id":"u_42","item_id":"item_7","event_type":"click"}`

	tests := []struct {
		name       string
		body       string
		produceErr error
		wantStatus int
		wantCalls  int
		wantKey    string
	}{
		{
			name:       "valid event accepted",
			body:       validBody,
			wantStatus: http.StatusAccepted,
			wantCalls:  1,
			wantKey:    "u_42",
		},
		{
			name:       "malformed json rejected",
			body:       `{"user_id":`,
			wantStatus: http.StatusBadRequest,
		},
		{
			name:       "validation failure rejected",
			body:       `{"user_id":"u_42","item_id":"item_7","event_type":"hover"}`,
			wantStatus: http.StatusBadRequest,
		},
		{
			name:       "empty body rejected",
			body:       ``,
			wantStatus: http.StatusBadRequest,
		},
		{
			name:       "producer failure surfaces as 503",
			body:       validBody,
			produceErr: errors.New("bus down"),
			wantStatus: http.StatusServiceUnavailable,
			wantCalls:  1,
		},
		{
			name:       "oversized body rejected as 413",
			body:       `{"user_id":"` + strings.Repeat("u", 1<<16+10) + `"}`,
			wantStatus: http.StatusRequestEntityTooLarge,
		},
		{
			name:       "padded ids are normalized before produce",
			body:       `{"user_id":" u42 ","item_id":"  i7  ","event_type":"click"}`,
			wantStatus: http.StatusAccepted,
			wantCalls:  1,
			wantKey:    "u42",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			fp := &fakeProducer{err: tt.produceErr}
			s := NewServer(fp, slog.New(slog.DiscardHandler))

			rec := post(s, tt.body)

			if rec.Code != tt.wantStatus {
				t.Fatalf("status = %d, want %d (body: %s)", rec.Code, tt.wantStatus, rec.Body.String())
			}
			if fp.calls != tt.wantCalls {
				t.Fatalf("producer calls = %d, want %d", fp.calls, tt.wantCalls)
			}
			if tt.wantKey != "" && fp.keys[0] != tt.wantKey {
				t.Fatalf("produce key = %q, want %q", fp.keys[0], tt.wantKey)
			}
			if tt.wantStatus == http.StatusAccepted && !strings.Contains(fp.last, `"created_at":"`) {
				t.Fatal("produced value missing server-set created_at")
			}
			if tt.name == "padded ids are normalized before produce" && strings.Contains(fp.last, `"item_id":"  i7  "`) {
				t.Fatal("produced value carries unpadded item_id")
			}
		})
	}
}

func TestHealthz(t *testing.T) {
	s := NewServer(&fakeProducer{}, slog.New(slog.DiscardHandler))
	rec := httptest.NewRecorder()
	s.Handler().ServeHTTP(rec, httptest.NewRequest(http.MethodGet, "/healthz", nil))
	if rec.Code != http.StatusOK {
		t.Fatalf("healthz status = %d, want 200", rec.Code)
	}
}
