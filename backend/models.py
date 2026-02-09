from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, BigInteger, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

class Stock(Base):
    """Stock model - stores ticker information"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prices = relationship('StockPrice', back_populates='stock', cascade='all, delete-orphan')
    backtests = relationship('Backtest', back_populates='stock', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StockPrice(Base):
    """Stock price model - stores historical OHLCV data"""
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    volume = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship('Stock', back_populates='prices')
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume
        }


class Backtest(Base):
    """Backtest model - stores backtest configuration and results"""
    __tablename__ = 'backtests'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Numeric(12, 2), nullable=False)
    final_value = Column(Numeric(12, 2))
    total_return = Column(Numeric(8, 4))
    max_drawdown = Column(Numeric(8, 4))
    sharpe_ratio = Column(Numeric(8, 4))
    num_trades = Column(Integer)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    stock = relationship('Stock', back_populates='backtests')
    trades = relationship('Trade', back_populates='backtest', cascade='all, delete-orphan')
    portfolio_history = relationship('PortfolioHistory', back_populates='backtest', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'ticker': self.stock.ticker if self.stock else None,
            'strategy_name': self.strategy_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'initial_capital': float(self.initial_capital) if self.initial_capital else None,
            'final_value': float(self.final_value) if self.final_value else None,
            'total_return': float(self.total_return) if self.total_return else None,
            'max_drawdown': float(self.max_drawdown) if self.max_drawdown else None,
            'sharpe_ratio': float(self.sharpe_ratio) if self.sharpe_ratio else None,
            'num_trades': self.num_trades,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Trade(Base):
    """Trade model - stores individual buy/sell trades"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    backtest_id = Column(Integer, ForeignKey('backtests.id'), nullable=False)
    trade_type = Column(String(10), nullable=False)  # 'BUY' or 'SELL'
    date = Column(Date, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    shares = Column(Numeric(12, 6), nullable=False)
    capital = Column(Numeric(12, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    backtest = relationship('Backtest', back_populates='trades')
    
    def to_dict(self):
        return {
            'id': self.id,
            'backtest_id': self.backtest_id,
            'trade_type': self.trade_type,
            'date': self.date.isoformat() if self.date else None,
            'price': float(self.price) if self.price else None,
            'shares': float(self.shares) if self.shares else None,
            'capital': float(self.capital) if self.capital else None
        }


class PortfolioHistory(Base):
    """Portfolio history model - stores daily portfolio values"""
    __tablename__ = 'portfolio_history'
    
    id = Column(Integer, primary_key=True)
    backtest_id = Column(Integer, ForeignKey('backtests.id'), nullable=False)
    date = Column(Date, nullable=False)
    portfolio_value = Column(Numeric(12, 2), nullable=False)
    stock_price = Column(Numeric(10, 2), nullable=False)
    shares_held = Column(Numeric(12, 6))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    backtest = relationship('Backtest', back_populates='portfolio_history')
    
    def to_dict(self):
        return {
            'id': self.id,
            'backtest_id': self.backtest_id,
            'date': self.date.isoformat() if self.date else None,
            'portfolio_value': float(self.portfolio_value) if self.portfolio_value else None,
            'stock_price': float(self.stock_price) if self.stock_price else None,
            'shares_held': float(self.shares_held) if self.shares_held else None
        }


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()