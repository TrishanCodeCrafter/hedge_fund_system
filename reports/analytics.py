import pandas as pd
from database.db import SessionLocal
from database.models import Trade, Security
import plotly.express as px

def get_trades_df():
    """Fetch all trades joined with security data."""
    db = SessionLocal()
    try:
        query = db.query(
            Trade.trade_date,
            Trade.trade_type,
            Trade.quantity,
            Trade.trade_price,
            Trade.principal_amount,
            Trade.trade_net_amount,
            Trade.commission,
            Security.symbol,
            Security.country,
            Security.asset_type
        ).outerjoin(Security, Trade.security_id == Security.security_id)
        
        # Using Pandas read_sql directly would be cleaner, but we can do it this way too
        df = pd.read_sql(query.statement, db.bind)
        return df
    finally:
        db.close()

def compute_net_transaction_flow(row):
    """
    Directional transaction-level capital flow/contribution analytics.
    Does not represent full portfolio accounting or realized/unrealized PnL.
    """
    net = row['trade_net_amount'] if pd.notnull(row['trade_net_amount']) else 0
    
    trade_type = str(row['trade_type']).lower()
    
    if 'sell' in trade_type or 'short' in trade_type:
        return net
    else:
        return -net

def prepare_analytics_data():
    """Prepare dataframe with net transaction flow."""
    df = get_trades_df()
    if df.empty:
        return df
    
    df['net_transaction_flow'] = df.apply(compute_net_transaction_flow, axis=1)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df['period_month'] = df['trade_date'].dt.to_period('M').astype(str)
    
    return df

def get_flow_by_stock(df):
    if df.empty: return pd.DataFrame()
    res = df.groupby('symbol')['net_transaction_flow'].sum().reset_index()
    return res.sort_values(by='net_transaction_flow', ascending=False)

def get_flow_by_country(df):
    if df.empty: return pd.DataFrame()
    res = df.groupby('country')['net_transaction_flow'].sum().reset_index()
    return res.sort_values(by='net_transaction_flow', ascending=False)

def get_flow_by_period(df):
    if df.empty: return pd.DataFrame()
    res = df.groupby('period_month')['net_transaction_flow'].sum().reset_index()
    return res.sort_values(by='period_month')

def get_top_positive_contributions(df, n=5):
    res = get_flow_by_stock(df)
    return res.head(n)

def get_top_negative_contributions(df, n=5):
    res = get_flow_by_stock(df)
    return res.tail(n).sort_values(by='net_transaction_flow', ascending=True)

# Plotly Charts
def plot_flow_by_stock(df):
    data = get_flow_by_stock(df)
    if data.empty: return None
    return px.bar(data, x='symbol', y='net_transaction_flow', title="Net Transaction Flow by Stock")

def plot_flow_by_country(df):
    data = get_flow_by_country(df)
    if data.empty: return None
    return px.pie(data, names='country', values='net_transaction_flow', title="Net Transaction Flow by Country")

def plot_flow_by_period(df):
    data = get_flow_by_period(df)
    if data.empty: return None
    return px.line(data, x='period_month', y='net_transaction_flow', title="Net Transaction Flow by Period")
