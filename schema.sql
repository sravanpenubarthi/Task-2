-- Product Management: database schema (SQLite)
-- The app creates this table automatically on startup; this file is for reference.

CREATE TABLE products (
    product_id   INTEGER      PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category     VARCHAR(100) NOT NULL,
    price        FLOAT        NOT NULL,
    quantity     INTEGER      NOT NULL,
    CONSTRAINT ck_products_price_positive    CHECK (price > 0),
    CONSTRAINT ck_products_quantity_positive CHECK (quantity > 0)
);

CREATE INDEX ix_products_category ON products (category);
