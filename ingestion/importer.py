import pandas as pd
import json
import os
import shutil
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from database.db import SessionLocal
from database.models import RawImport, Security, Trade
from .normalization import normalize_dataframe
from .mappings import clean_column_name

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

def process_file(file_path, source_system="System"):
    """
    Process the uploaded file, return ingestion stats.
    """
    stats = {
        'rows_imported': 0,
        'rows_normalized': 0,
        'rows_inserted': 0,
        'missing_optional_fields': [],
        'skipped_or_invalid_rows': 0,
        'mapped_columns_summary': []
    }
    
    file_name = os.path.basename(file_path)
    
    # Ensure upload dir exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # 1. Read File
    try:
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading file {file_name}: {e}")
        
    stats['rows_imported'] = len(df)
    
    # Copy file to uploads directory with timestamp for traceability
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    retained_file_name = f"{timestamp}_{file_name}"
    retained_file_path = os.path.join(UPLOAD_DIR, retained_file_name)
    shutil.copy2(file_path, retained_file_path)

    # 2. Store in raw_imports
    db = SessionLocal()
    raw_records = []
    
    # Store mapped summary
    original_cols = list(df.columns)
    mapped_cols = [clean_column_name(c) for c in original_cols]
    stats['mapped_columns_summary'] = list(zip(original_cols, mapped_cols))

    try:
        for idx, row in df.iterrows():
            # Filter out entirely null rows
            if row.dropna().empty:
                stats['skipped_or_invalid_rows'] += 1
                continue
            
            raw_data_json = row.to_json()
            raw_import = RawImport(
                source_file=retained_file_name,
                source_system=source_system,
                raw_data=raw_data_json
            )
            db.add(raw_import)
            raw_records.append(row)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    if not raw_records:
        return stats
        
    raw_df = pd.DataFrame(raw_records)

    # 3. Normalize Data
    normalized_df, missing_cols = normalize_dataframe(raw_df)
    stats['rows_normalized'] = len(normalized_df)
    stats['skipped_or_invalid_rows'] += len(raw_df) - len(normalized_df)
    stats['missing_optional_fields'] = missing_cols
    
    # 4. Insert into Securities (Upsert logic)
    securities_cache = {} # Map symbol -> security_id to reduce DB queries
    
    # Load existing securities
    existing_securities = db.query(Security).all()
    existing_securities_map = {}
    for sec in existing_securities:
        securities_cache[sec.symbol] = sec.security_id
        existing_securities_map[sec.symbol] = sec

    for _, row in normalized_df.iterrows():
        symbol = row['symbol']
        if not symbol:
            continue
            
        if symbol not in securities_cache:
            # Create new security
            new_sec = Security(
                symbol=symbol,
                investment_description=row['investment_description'],
                isin=row['isin'],
                bloomberg_ticker=row['bloomberg_ticker'],
                country=row['country'],
                asset_type=row['asset_type'],
                security_type=row['security_type'],
                trade_currency=row['trade_currency']
            )
            db.add(new_sec)
            try:
                db.commit()
                db.refresh(new_sec)
                securities_cache[symbol] = new_sec.security_id
            except IntegrityError:
                # Handle race condition or unexpected duplicates gracefully
                db.rollback()
                existing = db.query(Security).filter_by(symbol=symbol).first()
                if existing:
                    securities_cache[symbol] = existing.security_id
                    existing_securities_map[symbol] = existing
        else:
            # Update country if it was newly inferred and previously missing
            existing_sec = existing_securities_map.get(symbol)
            if existing_sec and not existing_sec.country and row.get('country'):
                existing_sec.country = row['country']
                db.add(existing_sec)
                db.commit()

    # 5. Insert into Trades
    trades_to_insert = []
    for _, row in normalized_df.iterrows():
        symbol = row['symbol']
        if not symbol or symbol not in securities_cache:
            stats['skipped_or_invalid_rows'] += 1
            continue
            
        trade = Trade(
            security_id=securities_cache[symbol],
            portfolio=row['portfolio'],
            fund=row['fund'],
            strategy=row['strategy'],
            trade_date=row['trade_date'],
            settle_date=row['settle_date'],
            trade_type=row['trade_type'],
            quantity=row['quantity'],
            trade_price=row['trade_price'],
            principal_amount=row['principal_amount'],
            trade_net_amount=row['trade_net_amount'],
            commission=row['commission'],
            fx_rate=row['fx_rate'],
            broker=row['broker'],
            custodian=row['custodian'],
            created_by=row['created_by'],
            source_file=retained_file_name,
            source_system=source_system
        )
        trades_to_insert.append(trade)

    if trades_to_insert:
        db.add_all(trades_to_insert)
        db.commit()
        stats['rows_inserted'] = len(trades_to_insert)
        
    db.close()
    
    return stats
