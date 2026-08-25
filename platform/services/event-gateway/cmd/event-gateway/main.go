// Command event-gateway ingests interaction events and publishes them to Kafka.
package main

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/hlm/content-personalization-mlops/platform/services/event-gateway/internal/broker"
	"github.com/hlm/content-personalization-mlops/platform/services/event-gateway/internal/gateway"
)

func env(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func main() {
	log := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	addr := env("GATEWAY_ADDR", ":8080")
	brokers := env("KAFKA_BOOTSTRAP_SERVERS", "localhost:29094")
	topic := env("GATEWAY_TOPIC", "mlops.events.raw")

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	producer, err := broker.New(ctx, brokers, topic)
	if err != nil {
		log.Error("broker init failed", "brokers", brokers, "err", err)
		os.Exit(1)
	}
	defer producer.Close()
	log.Info("connected to kafka", "brokers", brokers, "topic", topic)

	srv := &http.Server{
		Addr:              addr,
		Handler:           gateway.NewServer(producer, log).Handler(),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	shutdownDone := make(chan struct{})
	go func() {
		defer close(shutdownDone)
		<-ctx.Done()
		log.Info("shutting down")
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		_ = srv.Shutdown(shutdownCtx)
	}()

	if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Error("server exited", "err", err)
		os.Exit(1)
	}
	<-shutdownDone // drain in-flight handlers before closing the producer
}
