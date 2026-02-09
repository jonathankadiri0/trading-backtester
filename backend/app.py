from flask import Flask
from flask_cors import CORS
from config import Config
from models import init_db
from routes import api

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    # Initialize database
    with app.app_context():
        init_db()
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("Trading Backtester API Server")
    print("="*60)
    print("Server running at: http://localhost:5000")
    print("API endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/stocks              - Get all stocks")
    print("  GET  /api/backtests           - Get all backtests")
    print("  GET  /api/backtests/<id>      - Get backtest details")
    print("  POST /api/backtests/run       - Run new backtest")
    print("  DELETE /api/backtests/<id>    - Delete backtest")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)