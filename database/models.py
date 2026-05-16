from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class RawImport(Base):
    __tablename__ = 'raw_imports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_file = Column(String, nullable=False)
    source_system = Column(String)
    imported_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(Text, nullable=False)

class Security(Base):
    __tablename__ = 'securities'

    security_id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False)
    investment_description = Column(String)
    isin = Column(String)
    bloomberg_ticker = Column(String)
    country = Column(String)
    asset_type = Column(String)
    security_type = Column(String)
    trade_currency = Column(String)

    trades = relationship("Trade", back_populates="security")

class Trade(Base):
    __tablename__ = 'trades'

    trade_id = Column(Integer, primary_key=True, autoincrement=True)
    security_id = Column(Integer, ForeignKey('securities.security_id'))
    portfolio = Column(String)
    fund = Column(String)
    strategy = Column(String)
    trade_date = Column(Date)
    settle_date = Column(Date)
    trade_type = Column(String)
    quantity = Column(Float)
    trade_price = Column(Float)
    principal_amount = Column(Float)
    trade_net_amount = Column(Float)
    commission = Column(Float)
    fx_rate = Column(Float)
    broker = Column(String)
    custodian = Column(String)
    created_by = Column(String)
    source_file = Column(String)
    source_system = Column(String)

    security = relationship("Security", back_populates="trades")
