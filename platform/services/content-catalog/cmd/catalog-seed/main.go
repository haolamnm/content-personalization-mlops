package main

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/hlm/content-personalization-mlops/platform/services/content-catalog/internal/catalog"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()

	uri := envOrDefault("MONGODB_URI", "mongodb://localhost:27017/?authSource=admin")
	databaseName := envOrDefault("MONGODB_DATABASE", "mlops_catalog")
	collectionName := envOrDefault("MONGODB_COLLECTION", "content_items")
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(uri))
	if err != nil {
		log.Fatalf("connect MongoDB: %v", err)
	}
	defer func() { _ = client.Disconnect(context.Background()) }()
	if err := client.Ping(ctx, nil); err != nil {
		log.Fatalf("ping MongoDB: %v", err)
	}

	repository := catalog.NewMongoRepository(client.Database(databaseName), collectionName)
	if err := catalog.Seed(ctx, repository); err != nil {
		log.Fatalf("seed catalog: %v", err)
	}
	log.Printf("seeded catalog database=%s collection=%s", databaseName, collectionName)
}

func envOrDefault(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
