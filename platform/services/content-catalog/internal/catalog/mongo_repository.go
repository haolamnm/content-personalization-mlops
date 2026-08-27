package catalog

import (
	"context"
	"fmt"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// MongoRepository persists canonical content items in one MongoDB collection.
type MongoRepository struct {
	collection *mongo.Collection
}

// NewMongoRepository binds the catalog boundary to a database collection.
func NewMongoRepository(database *mongo.Database, collectionName string) *MongoRepository {
	return &MongoRepository{collection: database.Collection(collectionName)}
}

// GetByID reads one content item by its canonical interaction item_id.
func (r *MongoRepository) GetByID(ctx context.Context, id string) (ContentItem, error) {
	if id == "" {
		return ContentItem{}, fmt.Errorf("get content item: id is required")
	}
	var item ContentItem
	if err := r.collection.FindOne(ctx, bson.M{"_id": id}).Decode(&item); err != nil {
		if err == mongo.ErrNoDocuments {
			return ContentItem{}, ErrNotFound
		}
		return ContentItem{}, fmt.Errorf("get content item %q: %w", id, err)
	}
	return item, nil
}

// ListActive returns active items in stable newest-published order.
func (r *MongoRepository) ListActive(ctx context.Context, limit int) ([]ContentItem, error) {
	if limit <= 0 {
		return nil, fmt.Errorf("list active content items: limit must be positive")
	}
	cursor, err := r.collection.Find(
		ctx,
		bson.M{"status": StatusActive},
		options.Find().SetSort(bson.D{{Key: "published_at", Value: -1}, {Key: "_id", Value: 1}}).SetLimit(int64(limit)),
	)
	if err != nil {
		return nil, fmt.Errorf("list active content items: %w", err)
	}
	defer cursor.Close(ctx)

	items := make([]ContentItem, 0, limit)
	if err := cursor.All(ctx, &items); err != nil {
		return nil, fmt.Errorf("decode active content items: %w", err)
	}
	return items, nil
}

// Upsert validates and replaces one item without changing its canonical ID.
func (r *MongoRepository) Upsert(ctx context.Context, item ContentItem) error {
	if err := item.Validate(); err != nil {
		return err
	}
	_, err := r.collection.ReplaceOne(
		ctx,
		bson.M{"_id": item.ID},
		item,
		options.Replace().SetUpsert(true),
	)
	if err != nil {
		return fmt.Errorf("upsert content item %q: %w", item.ID, err)
	}
	return nil
}
