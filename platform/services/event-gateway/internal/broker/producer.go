// Package broker adapts the gateway to Kafka via franz-go.
package broker

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/twmb/franz-go/pkg/kgo"
)

// Producer implements gateway.Producer on top of a franz-go client.
type Producer struct {
	cl    *kgo.Client
	topic string
}

// New connects to the given seed brokers and targets topic.
func New(ctx context.Context, seedBrokers, topic string) (*Producer, error) {
	cl, err := kgo.NewClient(
		kgo.SeedBrokers(seedBrokers),
		kgo.DefaultProduceTopic(topic),
		kgo.WithLogger(kgo.BasicLogger(os.Stderr, kgo.LogLevelWarn, nil)),
	)
	if err != nil {
		return nil, fmt.Errorf("kafka client: %w", err)
	}
	// fail fast if no broker answers; caller decides policy
	if err := cl.Ping(ctx); err != nil {
		cl.Close()
		return nil, fmt.Errorf("kafka ping %s: %w", seedBrokers, err)
	}
	return &Producer{cl: cl, topic: topic}, nil
}

// Produce publishes value keyed by userID so per-user ordering holds.
func (p *Producer) Produce(userID string, value []byte) error {
	rec := &kgo.Record{Key: []byte(userID), Value: value}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := p.cl.ProduceSync(ctx, rec).FirstErr(); err != nil {
		return fmt.Errorf("produce to %s: %w", p.topic, err)
	}
	return nil
}

func (p *Producer) Close() { p.cl.Close() }
