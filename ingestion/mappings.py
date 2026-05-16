# ingestion/mappings.py

COLUMN_MAPPINGS = {
    # 2024 monthly transaction history.xlsx
    'Strategy': 'strategy',
    'Fund': 'fund',
    'Trans.Type': 'trade_type',
    'Broker': 'broker',
    'Symbol': 'symbol', # Note: Might need custom logic if it contains broker name like '2376 TT-Jefferies - Swap-CFD'
    'Quantity': 'quantity',
    'Price': 'trade_price',
    'Trade Date': 'trade_date',
    'Settle Date': 'settle_date',
    'Custodian': 'custodian',
    'Created By': 'created_by',

    # MMA_Trades format
    'Portfolio': 'portfolio',
    'TradeDate': 'trade_date',
    'SettleDate': 'settle_date',
    'TradeType': 'trade_type',
    'InvestmentID': 'symbol', # Alternative for symbol
    'InvestmentDescription': 'investment_description',
    'AssetType': 'asset_type',
    'SecurityType': 'security_type',
    'TradeCurrency': 'trade_currency',
    'FXRate': 'fx_rate',
    'TradeQuantity': 'quantity',
    'TradePrice': 'trade_price',
    'PrincipalAmount': 'principal_amount',
    'TotalCommission': 'commission',
    'TradeNetAmount': 'trade_net_amount',
    'BrokerCode': 'broker',
    'CustodianCode': 'custodian',
    'ISIN': 'isin',
    'BloombergTicker': 'bloomberg_ticker'
}

def clean_column_name(col_name):
    """Strip leading/trailing whitespace and return the normalized mapping if it exists."""
    if not isinstance(col_name, str):
        return str(col_name)
    cleaned = col_name.strip()
    return COLUMN_MAPPINGS.get(cleaned, cleaned)
