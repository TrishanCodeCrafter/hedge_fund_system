-- Raw Imports Table
CREATE TABLE IF NOT EXISTS raw_imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    source_system TEXT,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data TEXT NOT NULL
);

-- Securities Table
CREATE TABLE IF NOT EXISTS securities (
    security_id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT UNIQUE NOT NULL,
    investment_description TEXT,
    isin TEXT,
    bloomberg_ticker TEXT,
    country TEXT,
    asset_type TEXT,
    security_type TEXT,
    trade_currency TEXT
);

-- Trades Table
CREATE TABLE IF NOT EXISTS trades (
    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    security_id INTEGER,
    portfolio TEXT,
    fund TEXT,
    strategy TEXT,
    trade_date DATE,
    settle_date DATE,
    trade_type TEXT,
    quantity REAL,
    trade_price REAL,
    principal_amount REAL,
    trade_net_amount REAL,
    commission REAL,
    fx_rate REAL,
    broker TEXT,
    custodian TEXT,
    created_by TEXT,
    source_file TEXT,
    source_system TEXT,
    FOREIGN KEY(security_id) REFERENCES securities(security_id)
);
