# System Design

## Project Objective

The primary objective of this project is to build a lightweight, internal hedge fund trade analytics platform. The system is designed to seamlessly ingest heterogeneous financial trade exports (CSV/XLSX formats) from various operational or accounting systems, normalize these diverse formats into a unified relational schema, and generate reliable, directional analytical reports on a clean user interface.

## System Architecture

To achieve a modular, robust, and maintainable system, the architecture strictly separates concerns into distinct layers:

- **Ingestion Layer (`ingestion/importer.py`)**: Responsible for securely handling file uploads, persisting the raw source state, and orchestrating the normalization and insertion pipelines.
- **Normalization Layer (`ingestion/normalization.py` & `mappings.py`)**: Centralizes the logic required to map disparate source columns to our unified schema, standardize data types (dates, numeric fields), and execute metadata enrichment (e.g., country inference).
- **SQL Database Layer (`database/`)**: Utilizes SQLite via SQLAlchemy ORM to provide robust relational integrity.
- **Analytics/Reporting Layer (`reports/analytics.py`)**: Responsible for querying the normalized relational data and computing all required analytical metrics and data aggregations.
- **Streamlit UI Layer (`ui/dashboard.py` & `app.py`)**: Acts as the presentation tier, providing interactive dashboards, file upload capabilities, and visually appealing Plotly charts.

## Database Design Decisions

- **`raw_imports`**: Source rows are preserved in JSON format before normalization. This table exists primarily for auditability, traceability, and future reprocessing capabilities if the normalization logic requires changes.
- **`securities` and `trades` Separation**: We separate the transactional data (`trades`) from the asset master data (`securities`). This avoids duplicating security metadata across thousands of trades and ensures the analytics layer can accurately aggregate performance by asset.
- **Normalization for Maintainability**: By normalizing the data *before* it hits the analytics layer, we ensure that the reporting logic only ever has to interact with one unified, predictable schema, regardless of how many new external file formats are introduced to the ingestion layer in the future.

## Normalization Strategy

Financial trade exports inherently suffer from inconsistent schemas (e.g., `Trans.Type` vs `TradeType`).
Our normalization strategy employs a dynamic mapping system that standardizes these column headers. Furthermore, it gracefully handles optional or missing fields by populating `NULL` equivalents for downstream safety. 
We also implemented a ticker/country inference logic layer. Often, datasets lack explicit country fields. By parsing Bloomberg-style ticker suffixes (e.g., extracting `JT` from `6954 JT EQUITY` to infer `Japan`), we automatically enrich the dataset to support powerful geographic analytics without requiring manual user input.

## Analytics Assumptions

The provided datasets strictly contain transactional data and do **not** contain sufficient information to accurately calculate true realized PnL, unrealized PnL, cost-basis tracking, or market valuation history.
Therefore, the analytics layer intentionally implements **directional transaction-level capital flow approximations** (e.g., summing the net transaction amount directionally based on trade type). This approach was chosen to explicitly avoid making misleading investment performance claims while still providing valuable, directional capital-flow analytics.

## Future Extensibility

The modular architecture naturally supports future expansion:
- **Market Pricing Integration**: The `securities` table can easily be joined against an external API (like Bloomberg or Refinitiv) to fetch live pricing.
- **Position-Level Accounting**: By introducing a `positions` table that aggregates `trades`, the system could calculate full position-level performance and realized/unrealized PnL.
- **Additional Data Sources**: New file formats simply require adding a new mapping dictionary in `mappings.py` without requiring any changes to the UI or analytics layers.

## Engineering Priorities

The implementation heavily prioritized:
- **Maintainability & Modularity**: Clean separation of concerns allows developers to isolate debugging efforts.
- **Auditability**: Archiving raw imports guarantees data lineage.
- **Realistic Financial Data Handling**: Utilizing deterministic normalization strategies, schema mapping, and conservative reporting metrics.
- **Simplicity over Overengineering**: Implementing an effective Python/SQLite/Streamlit stack instead of unnecessarily complex microservices or containerized infrastructure.
