import streamlit as st
import pandas as pd
import os
import tempfile
from ingestion.importer import process_file
from reports.analytics import (
    prepare_analytics_data, get_flow_by_stock, get_flow_by_country,
    get_top_positive_contributions, get_top_negative_contributions, plot_flow_by_stock, plot_flow_by_country, plot_flow_by_period
)

def upload_page():
    st.header("📤 Upload Data")
    
    st.markdown("""
    Upload CSV or XLSX trade exports to ingest into the system.
    """)
    
    uploaded_files = st.file_uploader("Choose trade files", accept_multiple_files=True, type=['csv', 'xlsx'])
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if st.button(f"Import {uploaded_file.name}"):
                with st.spinner(f'Processing {uploaded_file.name}...'):
                    # Save to a temporary file for the importer
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    try:
                        stats = process_file(tmp_path, source_system="Manual Upload")
                        st.success(f"Successfully processed {uploaded_file.name}!")
                        
                        # Show Stats
                        st.subheader("Ingestion Summary")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Rows Imported", stats['rows_imported'])
                        col2.metric("Rows Normalized", stats['rows_normalized'])
                        col3.metric("Rows Inserted/Updated", stats['rows_inserted'])
                        
                        st.warning(f"Skipped/Invalid Rows: {stats['skipped_or_invalid_rows']}")
                        
                        with st.expander("View Normalization Mapping Summary"):
                            st.write("How columns were mapped:")
                            mapping_df = pd.DataFrame(stats['mapped_columns_summary'], columns=["Original Column", "Mapped Target"])
                            st.dataframe(mapping_df)
                            
                        if stats['missing_optional_fields']:
                            with st.expander("Unavailable Optional Fields"):
                                st.write(", ".join(stats['missing_optional_fields']))
                                
                    except Exception as e:
                        st.error(f"Error processing file: {e}")
                    finally:
                        os.unlink(tmp_path)


def trade_explorer_page():
    st.header("🔍 Trade Explorer")
    st.markdown("Browse and filter normalized trade records.")
    
    df = prepare_analytics_data()
    if df.empty:
        st.info("No trades found in the database. Upload data first.")
        return
        
    st.sidebar.subheader("Filters")
    
    # Date Range Filter
    min_date = df['trade_date'].dt.date.min() if not df['trade_date'].dropna().empty else None
    max_date = df['trade_date'].dt.date.max() if not df['trade_date'].dropna().empty else None
    
    date_range = None
    if min_date and max_date:
        date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    
    
    # Filters
    symbols = st.sidebar.multiselect("Symbols", options=df['symbol'].dropna().unique())
    countries = st.sidebar.multiselect("Countries", options=df['country'].dropna().unique())
    trade_types = st.sidebar.multiselect("Trade Types", options=df['trade_type'].dropna().unique())
    
    filtered_df = df.copy()
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['trade_date'].dt.date >= start_date) & (filtered_df['trade_date'].dt.date <= end_date)]
        
    if symbols:
        filtered_df = filtered_df[filtered_df['symbol'].isin(symbols)]
    if countries:
        filtered_df = filtered_df[filtered_df['country'].isin(countries)]
    if trade_types:
        filtered_df = filtered_df[filtered_df['trade_type'].isin(trade_types)]
        
    st.dataframe(filtered_df, use_container_width=True)


def analytics_page():
    st.header("📊 Analytics Dashboard")
    st.markdown("""
    > **Disclaimer**: This dashboard uses **directional transaction-level capital flow analytics** based on available trade data (`trade_net_amount`). 
    > It does **NOT** represent realized or unrealized portfolio performance, and it does **NOT** represent true security-level investment returns.
    """)
    
    df = prepare_analytics_data()
    if df.empty:
        st.info("No trades found in the database. Upload data first.")
        return
        
    st.sidebar.subheader("Filters")
    
    # Date Range Filter
    min_date = df['trade_date'].dt.date.min() if not df['trade_date'].dropna().empty else None
    max_date = df['trade_date'].dt.date.max() if not df['trade_date'].dropna().empty else None
    
    date_range = None
    if min_date and max_date:
        date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        
    filtered_df = df.copy()
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['trade_date'].dt.date >= start_date) & (filtered_df['trade_date'].dt.date <= end_date)]

    # Summary Metrics
    st.subheader("Summary Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Trades", len(filtered_df))
    m2.metric("Total Securities", filtered_df['symbol'].nunique())
    m3.metric("Total Net Transaction Flow", f"${filtered_df['net_transaction_flow'].sum():,.2f}")
    m4.metric("Countries Represented", filtered_df['country'].nunique())
    
    st.divider()
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Positive Trade Contributions (Selected Period)")
        st.dataframe(get_top_positive_contributions(filtered_df))
        
        fig1 = plot_flow_by_stock(filtered_df)
        if fig1: 
            fig1.update_layout(title="Net Transaction Flow by Stock (Selected Period)")
            st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("Top Negative Trade Contributions (Selected Period)")
        st.dataframe(get_top_negative_contributions(filtered_df))
        
        fig2 = plot_flow_by_country(filtered_df)
        if fig2: 
            fig2.update_layout(title="Net Transaction Flow by Country (Selected Period)")
            st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("Net Transaction Flow by Period")
    fig3 = plot_flow_by_period(filtered_df)
    if fig3: 
        fig3.update_layout(title="Net Transaction Flow by Period (Selected Period)")
        st.plotly_chart(fig3, use_container_width=True)
