# Hedge Fund Trade Analytics Platform

## Project Overview
A lightweight internal hedge fund trade analytics platform built with Python and Streamlit. The application seamlessly ingests heterogeneous financial trade export files (CSV/XLSX), normalizes them into a unified relational SQL schema, and generates directional, period-scoped transaction analytics on a responsive dashboard.

## Features
- **Trade File Ingestion**: Upload raw trade export files via the UI.
- **Normalization Pipeline**: Automatically standardizes varying column schemas, cleans numeric/date formats, and enriches data.
- **Country Inference**: Intelligently infers missing geographic data from Bloomberg-style ticker suffixes (e.g., `AMZN US`).
- **SQL Storage**: Persists normalized data using an SQLite database via SQLAlchemy.
- **Trade Explorer**: Browse, filter, and review normalized transaction records.
- **Analytics Dashboard**: View aggregate geographic and asset-level metrics dynamically visualized with Plotly.
- **Date Filtering**: Dynamically scope all tables and analytical metrics to a selected date range.
- **Transaction-Level Analytics**: Calculate directional capital-flow contributions per asset and region.

## Tech Stack
- **Python** (Core logic and orchestration)
- **Streamlit** (User Interface)
- **SQLite** (Relational Database)
- **SQLAlchemy** (ORM)
- **Pandas** (Data Processing)
- **Plotly** (Interactive Charting)

## Installation Instructions

1. Ensure Python 3.9+ is installed.
2. Clone the repository and navigate to the project root.
3. Install the dependencies:
```bash
pip install -r requirements.txt
```
4. Start the application:
```bash
streamlit run app.py
```
*(Note: If the database is completely empty upon startup, the system will attempt to automatically preload sample datasets from `data/raw/` if they exist.)*

## Upload Instructions
1. Navigate to the **Upload Data** tab in the Streamlit sidebar.
2. Upload one or multiple supported CSV/XLSX trade files.
3. Click "Import" for each file. 
4. The system will automatically map the columns, run normalization and inference logic, and insert the rows into the database. A summary metrics card will display the results of the import.
5. Navigate to the Analytics Dashboard to view the dynamically updated visualizations.

## Important Analytics Disclaimer
> The provided datasets strictly contain transactional export data. Therefore, the analytics produced by this system represent **transaction-level directional capital flow approximations**.
> They do **NOT** represent realized/unrealized investment returns, nor do they represent full portfolio accounting or precise Mark-to-Market (MTM) PnL.

## Project Structure
- `app.py`: Main Streamlit application entry point.
- `database/`: Contains the database connection utilities (`db.py`), SQLAlchemy models (`models.py`), and pure SQL representation (`schema.sql`).
- `ingestion/`: Houses the core data processing logic. Features `importer.py` for DB insertion, `normalization.py` for data cleaning, and `mappings.py` for column standardization.
- `reports/`: Contains `analytics.py`, which manages the logic to aggregate database transactions into reporting dataframes.
- `ui/`: Contains `dashboard.py` which dictates the layout and logic for the Streamlit UI.
- `data/raw/`: Directory intended for storing sample raw datasets (preloaded upon initialization).
- `uploads/`: System directory where the importer automatically archives timestamped copies of successfully ingested files.

## Future Improvements
- **Market Pricing Integration**: Integrating with an external API (like Bloomberg or Refinitiv) to retrieve live quotes and enable true MTM performance calculations.
- **Full Position-Level Accounting**: Building a continuous ledger system to track position costs over time rather than isolated transaction flows.
- **Expanded Analytics**: Generating metrics on portfolio risk exposure and volatility.

## Data Sensitivity Note
Original uploaded trade statement files are excluded from the public repository via `.gitignore` for strict financial data sensitivity and privacy considerations. 
