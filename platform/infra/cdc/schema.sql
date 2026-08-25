-- Content-personalization OLTP seed — idempotent; applied via:
--   docker exec -i data-postgres psql -U mlops -d mlops < platform/infra/cdc/schema.sql

CREATE TABLE IF NOT EXISTS public.interactions (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     text        NOT NULL,
    item_id     text        NOT NULL,
    event_type  text        NOT NULL CHECK (event_type IN ('impression', 'click', 'dwell', 'like', 'share')),
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS interactions_user_created_idx
    ON public.interactions (user_id, created_at DESC);
