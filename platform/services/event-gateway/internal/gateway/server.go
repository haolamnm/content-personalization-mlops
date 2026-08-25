package gateway

import (
	"encoding/json"
	"errors"
	"io"
	"log/slog"
	"net/http"
	"strings"
	"time"
)

// Producer is the outbound port: the gateway publishes events to the bus.
type Producer interface {
	Produce(userID string, value []byte) error
}

// Server serves the ingestion API.
type Server struct {
	producer Producer
	log      *slog.Logger
}

func NewServer(p Producer, log *slog.Logger) *Server {
	return &Server{producer: p, log: log}
}

// Handler returns the service mux: POST /events, GET /healthz.
func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /events", s.handleEvent)
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
	return mux
}

func (s *Server) handleEvent(w http.ResponseWriter, r *http.Request) {
	// events are tiny; refuse oversized bodies before decoding buffers them
	r.Body = http.MaxBytesReader(w, r.Body, 1<<16)
	var e Event
	if err := json.NewDecoder(r.Body).Decode(&e); err != nil {
		if _, ok := errors.AsType[*http.MaxBytesError](err); ok {
			http.Error(w, "body exceeds 64 KiB", http.StatusRequestEntityTooLarge)
			return
		}
		http.Error(w, "malformed JSON body", http.StatusBadRequest)
		return
	}
	// reject trailing garbage after the JSON value, not just the first value
	if err := json.NewDecoder(r.Body).Decode(&struct{}{}); err != io.EOF {
		http.Error(w, "malformed JSON body", http.StatusBadRequest)
		return
	}
	if err := e.Validate(); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// normalize: padded IDs would split per-user Kafka keys otherwise
	e.UserID = strings.TrimSpace(e.UserID)
	e.ItemID = strings.TrimSpace(e.ItemID)
	e.CreatedAt = time.Now().UTC()
	value, err := json.Marshal(e)
	if err != nil {
		s.log.Error("marshal event", "err", err)
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	if err := s.producer.Produce(e.UserID, value); err != nil {
		s.log.Error("produce event", "err", err)
		http.Error(w, "event bus unavailable", http.StatusServiceUnavailable)
		return
	}

	w.WriteHeader(http.StatusAccepted)
}
