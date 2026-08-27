//go:build integration

package catalog

import (
	"context"
	"os"
	"testing"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func TestMongoRepositoryReadsSeededCatalog(t *testing.T) {
	uri := os.Getenv("MONGODB_URI")
	if uri == "" {
		t.Skip("MONGODB_URI is not set")
	}
	databaseName := envOrDefault("MONGODB_DATABASE", "mlops_catalog_test")
	collectionName := envOrDefault("MONGODB_COLLECTION", "content_items")

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(uri))
	if err != nil {
		t.Fatalf("connect MongoDB: %v", err)
	}
	defer func() { _ = client.Disconnect(context.Background()) }()
	if err := client.Ping(ctx, nil); err != nil {
		t.Fatalf("ping MongoDB: %v", err)
	}

	repository := NewMongoRepository(client.Database(databaseName), collectionName)
	if err := Seed(ctx, repository); err != nil {
		t.Fatalf("seed MongoDB: %v", err)
	}

	item, err := repository.GetByID(ctx, "article-001")
	if err != nil {
		t.Fatalf("GetByID() error = %v", err)
	}
	if item.Title != "Building reliable feature pipelines" {
		t.Fatalf("GetByID() title = %q", item.Title)
	}

	active, err := repository.ListActive(ctx, 10)
	if err != nil {
		t.Fatalf("ListActive() error = %v", err)
	}
	if len(active) != 2 {
		t.Fatalf("ListActive() count = %d, want 2", len(active))
	}
}

func envOrDefault(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
