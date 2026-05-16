import pandas as pd
from .mappings import clean_column_name

COUNTRY_SUFFIX_MAP = {
    "JT": "Japan",
    "TT": "Taiwan",
    "KS": "South Korea",
    "US": "United States",
    "HK": "Hong Kong",
    "CH": "China",
    "LN": "United Kingdom",
    "CN": "Canada",
    "AU": "Australia"
}

def infer_country(row):
    """Infer country from existing value or symbol suffix."""
    original_symbol = str(row.get('original_symbol_for_inference', row.get('symbol', '')))
    
    # If country is already provided and not null, use it
    if pd.notnull(row.get('country')) and str(row['country']).strip() != "":
        return row['country']
        
    symbol_to_check = str(row.get('symbol', ''))
    # Example symbols: "6954 JT", "AMZN US", "2330 TT EQUITY"
    parts = symbol_to_check.split()
    inferred = None
    if len(parts) > 1:
        # Check suffixes like JT, US, etc.
        for part in parts[1:]:
            if part in COUNTRY_SUFFIX_MAP:
                inferred = COUNTRY_SUFFIX_MAP[part]
                break
                
    print(f"[Inference] Original Symbol: '{original_symbol}' | Inferred Country: {inferred} | Success: {inferred is not None}")
    return inferred


def normalize_dataframe(df):
    """
    Rename columns using the mappings.
    Filter to only those columns we care about in the schema.
    """
    # Rename columns
    df = df.rename(columns=lambda x: clean_column_name(x))
    
    # Optional fields to ensure exist with None
    target_columns = [
        'symbol', 'investment_description', 'isin', 'bloomberg_ticker', 'country', 'asset_type', 'security_type', 'trade_currency',
        'portfolio', 'fund', 'strategy', 'trade_date', 'settle_date', 'trade_type', 'quantity', 'trade_price', 
        'principal_amount', 'trade_net_amount', 'commission', 'fx_rate', 'broker', 'custodian', 'created_by'
    ]
    
    missing_cols = []
    
    for col in target_columns:
        if col not in df.columns:
            df[col] = None
            missing_cols.append(col)
            
    # Keep only the target columns
    # Drop rows where symbol is completely missing as it's our key identifier
    df = df.dropna(subset=['symbol'])

    # Save original symbol for logging before cleaning
    df['original_symbol_for_inference'] = df['symbol']
    
    # Clean up symbol if it has extra broker info attached (like '2376 TT-Jefferies - Swap-CFD')
    # A simple heuristic: split by '-' and take the first part
    df['symbol'] = df['symbol'].astype(str).apply(lambda x: x.split('-')[0].strip())
    
    # Infer country based on the cleaned symbol
    if 'country' in df.columns:
        print("\n--- Running Country Inference ---")
        df['country'] = df.apply(infer_country, axis=1)
        print("---------------------------------\n")
        
    # Drop the temporary column
    df = df.drop(columns=['original_symbol_for_inference'])
    
    # Convert dates to datetime objects
    for date_col in ['trade_date', 'settle_date']:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date

    # Convert numerics
    numeric_cols = ['quantity', 'trade_price', 'principal_amount', 'trade_net_amount', 'commission', 'fx_rate']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        
    # Replace NaNs with None for SQLAlchemy compatibility
    df = df.where(pd.notnull(df), None)
    
    return df, missing_cols
