import streamlit as st
import os
import glob
from database.db import init_db, SessionLocal
from database.models import RawImport
from ingestion.importer import process_file
from ui.dashboard import upload_page, trade_explorer_page, analytics_page

st.set_page_config(
    page_title="Hedge Fund Trade Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def preload_data_if_empty():
    """Check if db is empty, if so, load the initial sample data."""
    db = SessionLocal()
    count = db.query(RawImport).count()
    db.close()
    
    if count == 0:
        # DB is empty, let's preload from data/raw/
        raw_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'raw')
        if os.path.exists(raw_dir):
            files = glob.glob(os.path.join(raw_dir, '*.*'))
            for f in files:
                if f.endswith('.csv') or f.endswith('.xlsx'):
                    try:
                        process_file(f, source_system="System Preload")
                        st.sidebar.success(f"Preloaded {os.path.basename(f)}")
                    except Exception as e:
                        st.sidebar.error(f"Failed to preload {os.path.basename(f)}: {e}")

def main():
    st.sidebar.title("📈 Trade Analytics")
    
    if st.sidebar.button("Rebuild Database"):
        db = SessionLocal()
        db.close()
        from database.db import engine
        engine.dispose()
        try:
            os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hedge_fund.db'))
            st.sidebar.success("Database deleted. Please refresh the page.")
        except Exception as e:
            st.sidebar.error(f"Failed to delete DB: {e}")
    
    # Initialize DB on first run
    init_db()
    
    # Preload sample data if needed
    preload_data_if_empty()
    
    # Navigation
    pages = {
        "Upload Data": upload_page,
        "Trade Explorer": trade_explorer_page,
        "Analytics Dashboard": analytics_page
    }
    
    selection = st.sidebar.radio("Navigate", list(pages.keys()))
    
    # Render selected page
    pages[selection]()

if __name__ == "__main__":
    main()
