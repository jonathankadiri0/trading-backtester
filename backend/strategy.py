import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from models import Stock, StockPrice, Backtest, Trade, PortfolioHistory

class MovingAverageCrossover:
    """
    Moving Average Crossover Strategy
    
    Buy Signal: When short-term MA crosses above long-term MA
    Sell Signal: When short-term MA crosses below long-term MA
    """
    
    def __init__(self, db_session, ticker, start_date, end_date, 
                 initial_capital=10000, short_window=20, long_window=50):
        """
        Initialize the strategy
        
        Args:
            db_session: SQLAlchemy database session
            ticker: Stock ticker symbol
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)
            initial_capital: Starting capital in dollars
            short_window: Short-term moving average period
            long_window: Long-term moving average period
        """
        self.db = db_session
        self.ticker = ticker.upper()
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.short_window = short_window
        self.long_window = long_window
        self.stock = None
        self.backtest = None
        
    def fetch_and_store_data(self):
        """Fetch historical data from Yahoo Finance and store in database"""
        print(f"Fetching data for {self.ticker}...")
        
        # Check if stock exists in database
        self.stock = self.db.query(Stock).filter_by(ticker=self.ticker).first()
        
        if not self.stock:
            # Create new stock entry
            self.stock = Stock(ticker=self.ticker)
            self.db.add(self.stock)
            self.db.commit()
            print(f"Created new stock entry for {self.ticker}")
        
        # Fetch data from Yahoo Finance
        df = yf.download(self.ticker, start=self.start_date, end=self.end_date, progress=False)
        
        if len(df) == 0:
            raise ValueError(f"No data found for {self.ticker}")
        
        # Store price data in database
        for date, row in df.iterrows():
            # Check if price data already exists
            existing_price = self.db.query(StockPrice).filter_by(
                stock_id=self.stock.id,
                date=date.date()
            ).first()
            
            if not existing_price:
                price = StockPrice(
                    stock_id=self.stock.id,
                    date=date.date(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                )
                self.db.add(price)
        
        self.db.commit()
        print(f"Stored {len(df)} days of price data")
        
        return df
    
    def calculate_signals(self, df):
        """Calculate moving averages and generate trading signals"""
        # Make a copy to avoid SettingWithCopyWarning
        df = df.copy()
        
        # Calculate moving averages
        df['SMA_short'] = df['Close'].rolling(window=self.short_window).mean()
        df['SMA_long'] = df['Close'].rolling(window=self.long_window).mean()
        
        # Generate position signals using numpy where instead of loc
        df['Signal'] = np.where(df['SMA_short'] > df['SMA_long'], 1, -1)
        
        # Identify crossover points (actual trading signals)
        df['Position'] = df['Signal'].diff()
        
        # Drop rows with NaN (insufficient data for MA calculation)
        df = df.dropna()
        
        return df
    
    def run_backtest(self):
        """Execute the backtest strategy"""
        print(f"\n{'='*60}")
        print(f"Running backtest for {self.ticker}")
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Strategy: MA Crossover ({self.short_window}/{self.long_window})")
        print(f"{'='*60}\n")
        
        # Fetch and prepare data
        df = self.fetch_and_store_data()
        df = self.calculate_signals(df)
        
        # Create backtest record
        self.backtest = Backtest(
            stock_id=self.stock.id,
            strategy_name=f"MA_Crossover_{self.short_window}_{self.long_window}",
            start_date=self.start_date,
            end_date=self.end_date,
            initial_capital=self.initial_capital,
            status='running'
        )
        self.db.add(self.backtest)
        self.db.commit()
        
        # Execute backtest simulation
        capital = self.initial_capital
        shares = 0
        trade_count = 0
        
        for date, row in df.iterrows():
            # Extract scalar values from pandas Series
            position_value = float(row['Position'])
            close_price = float(row['Close'])
            
            # Buy signal: short MA crosses above long MA
            if position_value == 2 and capital > 0:  # Position changed from -1/0 to 1
                shares = capital / close_price
                capital = 0
                trade_count += 1
                
                # Record trade
                trade = Trade(
                    backtest_id=self.backtest.id,
                    trade_type='BUY',
                    date=date.date(),
                    price=close_price,
                    shares=float(shares),
                    capital=0
                )
                self.db.add(trade)
                print(f"BUY  | {date.date()} | Price: ${close_price:.2f} | Shares: {shares:.2f}")
            
            # Sell signal: short MA crosses below long MA
            elif position_value == -2 and shares > 0:  # Position changed from 1 to -1/0
                capital = shares * close_price
                shares = 0
                trade_count += 1
                
                # Record trade
                trade = Trade(
                    backtest_id=self.backtest.id,
                    trade_type='SELL',
                    date=date.date(),
                    price=close_price,
                    shares=0,
                    capital=float(capital)
                )
                self.db.add(trade)
                print(f"SELL | {date.date()} | Price: ${close_price:.2f} | Capital: ${capital:.2f}")
            
            # Record daily portfolio value
            portfolio_value = capital + (shares * close_price)
            portfolio_hist = PortfolioHistory(
                backtest_id=self.backtest.id,
                date=date.date(),
                portfolio_value=float(portfolio_value),
                stock_price=close_price,
                shares_held=float(shares)
            )
            self.db.add(portfolio_hist)
        
        self.db.commit()
        
        # Calculate performance metrics
        self.calculate_metrics(df)
        
        return self.backtest
    
    def calculate_metrics(self, df):
        """Calculate and store performance metrics"""
        # Get portfolio history
        portfolio_history = self.db.query(PortfolioHistory).filter_by(
            backtest_id=self.backtest.id
        ).order_by(PortfolioHistory.date).all()
        
        portfolio_values = [float(p.portfolio_value) for p in portfolio_history]
        final_value = portfolio_values[-1]
        
        # Total return
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        # Buy and hold return
        first_price = float(df['Close'].iloc[0])
        last_price = float(df['Close'].iloc[-1])
        buy_hold_return = ((last_price - first_price) / first_price) * 100
        
        # Max drawdown
        portfolio_array = np.array(portfolio_values)
        running_max = np.maximum.accumulate(portfolio_array)
        drawdown = (portfolio_array - running_max) / running_max
        max_drawdown = float(drawdown.min() * 100)
        
        # Sharpe ratio
        returns = pd.Series(portfolio_values).pct_change().dropna()
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = float((returns.mean() / returns.std()) * np.sqrt(252))
        else:
            sharpe_ratio = 0.0
        
        # Number of trades
        num_trades = self.db.query(Trade).filter_by(backtest_id=self.backtest.id).count()
        
        # Update backtest record
        self.backtest.final_value = final_value
        self.backtest.total_return = total_return
        self.backtest.max_drawdown = max_drawdown
        self.backtest.sharpe_ratio = sharpe_ratio
        self.backtest.num_trades = num_trades
        self.backtest.status = 'completed'
        self.backtest.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        # Print results
        print(f"\n{'='*60}")
        print(f"BACKTEST RESULTS")
        print(f"{'='*60}")
        print(f"Initial Capital:        ${self.initial_capital:,.2f}")
        print(f"Final Value:            ${final_value:,.2f}")
        print(f"Total Return:           {total_return:.2f}%")
        print(f"Buy & Hold Return:      {buy_hold_return:.2f}%")
        print(f"Max Drawdown:           {max_drawdown:.2f}%")
        print(f"Sharpe Ratio:           {sharpe_ratio:.2f}")
        print(f"Number of Trades:       {num_trades}")
        print(f"{'='*60}\n")