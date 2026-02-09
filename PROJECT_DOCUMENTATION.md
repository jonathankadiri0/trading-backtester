# Trading Backtester

A full-stack app that tests algorithmic trading strategies on real stock data.

## What It Does

- Tests Moving Average Crossover strategy on stocks
- Fetches real market data from Yahoo Finance
- Calculates performance metrics (returns, Sharpe ratio, drawdown)
- Stores everything in PostgreSQL database

## Tech Stack

**Backend:** Python, Flask, PostgreSQL, SQLAlchemy, pandas, yfinance

## File Structure

```
backend/
├── app.py           # Flask server
├── config.py        # Database settings
├── models.py        # Database tables
├── routes.py        # API endpoints
├── strategy.py      # Trading logic
├── requirements.txt # Dependencies
└── .env            # DB password (not in Git)
```

## How It Works

1. User sends stock ticker + dates to API
2. Backend fetches historical prices from Yahoo Finance
3. Strategy calculates moving averages
4. Simulates buy/sell based on crossovers
5. Stores trades in database
6. Returns performance results

## Setup

```bash
# Install PostgreSQL, create database 'trading_backtester'

cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

# Create .env file with DB password
python app.py  # Server runs on http://localhost:5000
```

## API Example

**Run Backtest:**

```json
POST http://localhost:5000/api/backtests/run

{
  "ticker": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-12-01",
  "initial_capital": 10000
}
```

**Response:**

```json
{
  "final_value": 12453.7,
  "total_return": 24.54,
  "sharpe_ratio": 1.62,
  "num_trades": 4
}
```

## Problems We Solved

1. **Wrong DB Port**: PostgreSQL on 5433 not 5432 → checked pgAdmin
2. **yfinance Errors**: Updated library with `pip install --upgrade yfinance`
3. **Pandas Series Error**: Can't use Series in `if` statements → converted to `float()`
4. **Git Bash**: Used `source venv/Scripts/activate` not backslashes

## Trading Strategy

**Moving Average Crossover:**

- Buy when short MA (20 days) crosses above long MA (50 days)
- Sell when short MA crosses below long MA
- Simple but effective for trending markets

## First Test Results (AAPL 2024)

- Started: $10,000
- Ended: $12,453.70
- Profit: $2,453.70 (24.54%)
- Risk: Sharpe 1.62, Drawdown -11.75%
