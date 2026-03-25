#!/usr/bin/env bash
set -euo pipefail

# Seed script for local development database
# Creates schemas and inserts sample data for all services

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-shelflife}"
DB_PASSWORD="${DB_PASSWORD:-shelflife}"

export PGPASSWORD="$DB_PASSWORD"

echo "=== ShelfLife Database Seed ==="
echo "Host: $DB_HOST:$DB_PORT"

# Create service databases
for db in orders inventory analytics auth; do
    echo "Creating database: $db"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d shelflife -c "CREATE DATABASE $db;" 2>/dev/null || true
done

# Seed orders database
echo "Seeding orders database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d orders <<'SQL'
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    customer_id VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_cents INTEGER NOT NULL DEFAULT 0,
    priority BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id UUID REFERENCES orders(id),
    sku VARCHAR(64) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
SQL

# Seed inventory database
echo "Seeding inventory database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d inventory <<'SQL'
CREATE TABLE IF NOT EXISTS stock_levels (
    sku VARCHAR(64) PRIMARY KEY,
    qty INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stock_audit (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(64) NOT NULL,
    delta INTEGER NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Insert sample stock
INSERT INTO stock_levels (sku, qty) VALUES
    ('SKU-WIDGET-001', 500),
    ('SKU-WIDGET-002', 250),
    ('SKU-GADGET-001', 1000),
    ('SKU-GADGET-002', 75),
    ('SKU-SUPPLY-001', 10000)
ON CONFLICT (sku) DO NOTHING;
SQL

# Seed analytics database
echo "Seeding analytics database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d analytics <<'SQL'
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    source VARCHAR(64) NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rollups_hourly (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(64) NOT NULL,
    hour TIMESTAMP NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    UNIQUE(event_type, hour)
);

CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_ingested ON events(ingested_at);
SQL

echo "=== Seed complete ==="
