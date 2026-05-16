# Hedge Fund Trade Analytics Platform

## Objective

Build a lightweight internal hedge fund trade analytics platform using:

* Python
* Streamlit
* SQLite
* SQLAlchemy
* Pandas

The system should ingest multiple inconsistent financial trade export files (CSV/XLSX), normalize them into a unified SQL schema, and generate analytical reports.

The uploaded files represent transaction exports from different operational/accounting systems used by a hedge fund.

This project should feel like a realistic internal financial analytics tool, not a toy CRUD application.

---

# Core Goals

Prioritize:

* clean architecture
* normalized database design
* maintainability
* auditability
* modular analytics
* simplicity over overengineering

Avoid:

* React/frontend frameworks
* cloud infrastructure
* authentication systems
* microservices
* Docker
* unnecessary complexity

---

# Required Tech Stack

## Backend

* Python

## Database

* SQLite

## ORM

* SQLAlchemy

## Frontend / GUI

* Streamlit

## Data Processing

* Pandas

## Optional

* Plotly (for charts)

---

# Expected Project Structure

```plaintext
hedge_fund_system/
│
├── app.py
├── requirements.txt
├── README.md
│
├── database/
│   ├── db.py
│   ├── models.py
│   ├── schema.sql
│
├── ingestion/
│   ├── importer.py
│   ├── normalization.py
│   ├── mappings.py
│
├── reports/
│   ├── analytics.py
│
├── ui/
│   ├── dashboard.py
│
├── data/
│   ├── raw/
│
└── uploads/
```

---

# Database Design

## 1. raw_imports

Purpose:
Preserve imported source rows before normalization.

Each row from an imported file should become one row in this table.

This table exists for:

* auditability
* traceability
* future reprocessing

### Fields

* id
* source_file
* source_system
* imported_at
* raw_data

`raw_data` should store the original row as JSON/text.

---

## 2. securities

Purpose:
Normalized security master table.

Avoid duplicate securities.

### Fields

* security_id
* symbol
* investment_description
* isin
* bloomberg_ticker
* country
* asset_type
* security_type
* trade_currency

Only include fields that exist in the provided source files.

---

## 3. trades

Purpose:
Normalized transactional trade table.

### Fields

* trade_id
* security_id (foreign key)
* portfolio
* fund
* strategy
* trade_date
* settle_date
* trade_type
* quantity
* trade_price
* principal_amount
* trade_net_amount
* commission
* fx_rate
* broker
* custodian
* created_by
* source_file
* source_system

Allow NULL values where fields are unavailable in some source files.

---

# Normalization Layer

Create a normalization layer that maps inconsistent source column names into unified schema fields.

Examples:

| Source Column | Normalized Column |
| ------------- | ----------------- |
| TradeDate     | trade_date        |
| Trade Date    | trade_date        |
| InvestmentID  | symbol            |
| Symbol        | symbol            |
| TradeType     | trade_type        |
| Trans.Type    | trade_type        |

The normalization layer is a core part of the project.

The goal is:
heterogeneous financial exports → unified analytical schema.

---

# Data Ingestion Workflow

The system should:

1. Upload CSV/XLSX files
2. Preview uploaded data
3. Validate columns
4. Store raw rows in `raw_imports`
5. Normalize data
6. Insert normalized records into:

   * securities
   * trades

Track:

* source_file
* source_system

---

# Reporting Requirements

Create analytical reports for:

1. Return by Stock
2. Return by Country
3. Return by Period
4. Top 5 Winners
5. Top 5 Losers

---

# Important Reporting Assumption

The provided datasets do NOT contain full portfolio accounting or realized/unrealized PnL logic.

Implement a simplified transaction-level return approximation using:

* trade_net_amount
* principal_amount
* trade direction

Document all assumptions clearly in the README.

The reporting system should be modular and easy to extend later.

---

# Streamlit Dashboard

Create a clean Streamlit dashboard with these sections/pages:

## 1. Upload Data

Features:

* upload CSV/XLSX
* preview imported rows
* import button

---

## 2. Trade Explorer

Features:

* searchable/filterable trades
* symbol filters
* country filters
* date filters
* trade type filters

---

## 3. Analytics Dashboard

Features:

* Return by Stock
* Return by Country
* Return by Period
* Top Winners
* Top Losers
* charts
* sortable tables

The UI should be:

* clean
* analytical
* professional
* minimal

---

# README Requirements

Create a detailed README explaining:

* project architecture
* database schema
* normalization strategy
* ingestion workflow
* reporting assumptions
* future extensibility ideas

Explain WHY architectural decisions were made.

---

# Engineering Expectations

Prioritize:

* readable code
* modularity
* separation of concerns
* maintainability
* realistic financial data architecture

The final result should resemble a lightweight internal hedge fund analytics tool.
