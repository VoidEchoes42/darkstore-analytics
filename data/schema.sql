-- =============================================================================
-- Darkstore Analytics — Database Schema
-- Modeled on Blinkit's quick-commerce dark store delivery model
-- =============================================================================

-- Drop existing tables (safe for development; remove in production)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS delivery_partners CASCADE;
DROP TABLE IF EXISTS product_store_inventory CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

-- =============================================================================
-- 1. CATEGORIES
-- =============================================================================
CREATE TABLE categories (
    category_id      SERIAL PRIMARY KEY,
    category_name    VARCHAR(100) NOT NULL UNIQUE,
    parent_category  VARCHAR(100),
    is_perishable    BOOLEAN DEFAULT FALSE,
    shelf_life_days  INT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 2. STORES (Dark Stores)
-- =============================================================================
CREATE TABLE stores (
    store_id         SERIAL PRIMARY KEY,
    store_name       VARCHAR(100) NOT NULL,
    city             VARCHAR(50) NOT NULL,
    zone             VARCHAR(50) NOT NULL,
    address          TEXT,
    latitude         DECIMAL(9,6),
    longitude        DECIMAL(9,6),
    capacity_orders_per_hour INT NOT NULL DEFAULT 60,
    capacity_orders_per_day  INT NOT NULL DEFAULT 600,
    sla_target_minutes       INT NOT NULL DEFAULT 10,
    is_active        BOOLEAN DEFAULT TRUE,
    opened_at        DATE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_capacity CHECK (capacity_orders_per_hour > 0),
    CONSTRAINT valid_sla CHECK (sla_target_minutes > 0)
);

CREATE INDEX idx_stores_city ON stores(city);
CREATE INDEX idx_stores_zone ON stores(zone);

-- =============================================================================
-- 3. PRODUCTS
-- =============================================================================
CREATE TABLE products (
    product_id           SERIAL PRIMARY KEY,
    product_name         VARCHAR(200) NOT NULL,
    category_id          INT NOT NULL REFERENCES categories(category_id),
    brand                VARCHAR(100),
    unit                 VARCHAR(20),          -- e.g., "1L", "500g", "pack of 6"
    mrp                  DECIMAL(10,2) NOT NULL,
    selling_price        DECIMAL(10,2) NOT NULL,
    cost_price           DECIMAL(10,2),
    weight_grams         INT,
    is_available         BOOLEAN DEFAULT TRUE,
    abc_class            VARCHAR(1),           -- A/B/C (filled by analytics)
    xyz_class            VARCHAR(1),           -- X/Y/Z (filled by analytics)
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_abc ON products(abc_class);

-- =============================================================================
-- 4. CUSTOMERS
-- =============================================================================
CREATE TABLE customers (
    customer_id          SERIAL PRIMARY KEY,
    phone_number         VARCHAR(15) NOT NULL UNIQUE,
    name                 VARCHAR(100),
    city                 VARCHAR(50) NOT NULL,
    zone                 VARCHAR(50),
    signup_date          DATE NOT NULL,
    acquisition_channel  VARCHAR(50) NOT NULL, -- organic / referral / paid_ads / offline
    total_orders         INT DEFAULT 0,
    total_gmv            DECIMAL(12,2) DEFAULT 0,
    is_active            BOOLEAN DEFAULT TRUE,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_channel CHECK (
        acquisition_channel IN ('organic', 'referral', 'paid_ads', 'offline')
    )
);

CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_customers_signup ON customers(signup_date);
CREATE INDEX idx_customers_channel ON customers(acquisition_channel);

-- =============================================================================
-- 5. DELIVERY PARTNERS
-- =============================================================================
CREATE TABLE delivery_partners (
    partner_id           SERIAL PRIMARY KEY,
    name                 VARCHAR(100) NOT NULL,
    phone_number         VARCHAR(15) NOT NULL UNIQUE,
    city                 VARCHAR(50) NOT NULL,
    zone                 VARCHAR(50),
    vehicle_type         VARCHAR(20),          -- bike / scooter / cycle
    shift_start_time     TIME,
    shift_end_time       TIME,
    is_active            BOOLEAN DEFAULT TRUE,
    joined_at            DATE,
    avg_rating           DECIMAL(2,1) DEFAULT 4.0,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partners_city ON delivery_partners(city);
CREATE INDEX idx_partners_zone ON delivery_partners(zone);

-- =============================================================================
-- 6. PRODUCT STORE INVENTORY
-- =============================================================================
CREATE TABLE product_store_inventory (
    inventory_id         SERIAL PRIMARY KEY,
    store_id             INT NOT NULL REFERENCES stores(store_id),
    product_id           INT NOT NULL REFERENCES products(product_id),
    stock_quantity       INT NOT NULL DEFAULT 0,
    reorder_level        INT DEFAULT 10,
    last_restocked_at    TIMESTAMP,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(store_id, product_id)
);

CREATE INDEX idx_inventory_store ON product_store_inventory(store_id);
CREATE INDEX idx_inventory_product ON product_store_inventory(product_id);

-- =============================================================================
-- 7. ORDERS
-- =============================================================================
CREATE TABLE orders (
    order_id             BIGSERIAL PRIMARY KEY,
    customer_id          INT NOT NULL REFERENCES customers(customer_id),
    store_id             INT NOT NULL REFERENCES stores(store_id),
    partner_id           INT REFERENCES delivery_partners(partner_id),
    order_status         VARCHAR(20) NOT NULL DEFAULT 'placed',
    -- Statuses: placed → picked → packed → dispatched → delivered
    --           (or cancelled)
    order_placed_at      TIMESTAMP NOT NULL,
    picked_at            TIMESTAMP,
    packed_at            TIMESTAMP,
    dispatched_at        TIMESTAMP,
    delivered_at         TIMESTAMP,
    cancelled_at         TIMESTAMP,
    cancellation_reason  VARCHAR(200),
    sla_target_minutes   INT,
    actual_delivery_minutes INT,             -- computed: delivered - placed
    is_rain_flag         BOOLEAN DEFAULT FALSE,
    is_holiday_flag      BOOLEAN DEFAULT FALSE,
    payment_mode         VARCHAR(20),         -- upi / cash / card / wallet
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_status CHECK (
        order_status IN (
            'placed', 'picked', 'packed', 'dispatched',
            'delivered', 'cancelled'
        )
    ),
    CONSTRAINT valid_delivery_time CHECK (
        (delivered_at IS NULL) OR
        (actual_delivery_minutes IS NULL) OR
        (EXTRACT(EPOCH FROM (delivered_at - order_placed_at)) / 60 = actual_delivery_minutes)
    )
);

CREATE INDEX idx_orders_store_time ON orders(store_id, order_placed_at);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_placed_at ON orders(order_placed_at);

-- =============================================================================
-- 8. ORDER ITEMS
-- =============================================================================
CREATE TABLE order_items (
    order_item_id        BIGSERIAL PRIMARY KEY,
    order_id             BIGINT NOT NULL REFERENCES orders(order_id),
    product_id           INT NOT NULL REFERENCES products(product_id),
    quantity             INT NOT NULL DEFAULT 1,
    unit_price           DECIMAL(10,2) NOT NULL,
    discount_amount      DECIMAL(10,2) DEFAULT 0,
    total_price          DECIMAL(10,2) NOT NULL,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_quantity CHECK (quantity > 0),
    CONSTRAINT positive_price CHECK (unit_price > 0)
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- =============================================================================
-- HELPER: ER Diagram (Mermaid syntax)
-- Paste into GitHub Mermaid renderer or Mermaid Live Editor
-- =============================================================================
/*
erDiagram
    categories ||--o{ products : "has"
    stores ||--o{ orders : "fulfills"
    stores ||--o{ product_store_inventory : "holds"
    customers ||--o{ orders : "places"
    delivery_partners ||--o{ orders : "delivers"
    orders ||--|{ order_items : "contains"
    products ||--|{ order_items : "appears_in"
    products ||--o{ product_store_inventory : "stocked_at"
*/
