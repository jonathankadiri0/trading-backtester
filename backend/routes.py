from flask import Blueprint, request, jsonify
from models import SessionLocal, Stock, Backtest, Trade, PortfolioHistory
from strategy import MovingAverageCrossover
from datetime import datetime
from sqlalchemy import desc
import traceback

api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Trading Backtester API is running'}), 200


@api.route('/stocks', methods=['GET'])
def get_stocks():
    """Get all stocks in database"""
    db = SessionLocal()
    try:
        stocks = db.query(Stock).all()
        return jsonify([stock.to_dict() for stock in stocks]), 200
    finally:
        db.close()


@api.route('/backtests', methods=['GET'])
def get_backtests():
    """Get all backtests"""
    db = SessionLocal()
    try:
        backtests = db.query(Backtest).order_by(desc(Backtest.created_at)).all()
        return jsonify([bt.to_dict() for bt in backtests]), 200
    finally:
        db.close()


@api.route('/backtests/<int:backtest_id>', methods=['GET'])
def get_backtest(backtest_id):
    """Get specific backtest details"""
    db = SessionLocal()
    try:
        backtest = db.query(Backtest).filter_by(id=backtest_id).first()
        
        if not backtest:
            return jsonify({'error': 'Backtest not found'}), 404
        
        # Get trades
        trades = db.query(Trade).filter_by(backtest_id=backtest_id).all()
        
        # Get portfolio history
        portfolio_history = db.query(PortfolioHistory).filter_by(
            backtest_id=backtest_id
        ).order_by(PortfolioHistory.date).all()
        
        return jsonify({
            'backtest': backtest.to_dict(),
            'trades': [trade.to_dict() for trade in trades],
            'portfolio_history': [ph.to_dict() for ph in portfolio_history]
        }), 200
    finally:
        db.close()


@api.route('/backtests/run', methods=['POST'])
def run_backtest():
    """
    Run a new backtest
    
    Request body:
    {
        "ticker": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "initial_capital": 10000,
        "short_window": 20,
        "long_window": 50
    }
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['ticker', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Extract parameters with defaults
    ticker = data['ticker'].upper()
    start_date = data['start_date']
    end_date = data['end_date']
    initial_capital = data.get('initial_capital', 10000)
    short_window = data.get('short_window', 20)
    long_window = data.get('long_window', 50)
    
    # Validate dates
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start >= end:
            return jsonify({'error': 'Start date must be before end date'}), 400
            
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate windows
    if short_window >= long_window:
        return jsonify({'error': 'Short window must be less than long window'}), 400
    
    # Run backtest
    db = SessionLocal()
    try:
        strategy = MovingAverageCrossover(
            db_session=db,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            short_window=short_window,
            long_window=long_window
        )
        
        backtest = strategy.run_backtest()
        
        return jsonify({
            'message': 'Backtest completed successfully',
            'backtest': backtest.to_dict()
        }), 201
        
    except Exception as e:
        traceback.print_exc()  # Print full error to terminal
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@api.route('/backtests/<int:backtest_id>', methods=['DELETE'])
def delete_backtest(backtest_id):
    """Delete a backtest and all related data"""
    db = SessionLocal()
    try:
        backtest = db.query(Backtest).filter_by(id=backtest_id).first()
        
        if not backtest:
            return jsonify({'error': 'Backtest not found'}), 404
        
        db.delete(backtest)
        db.commit()
        
        return jsonify({'message': 'Backtest deleted successfully'}), 200
    finally:
        db.close()