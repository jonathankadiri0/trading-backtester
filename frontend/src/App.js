import React, { useState } from 'react';
import './App.css';
import BacktestForm from './components/BacktestForm';
import ResultsDisplay from './components/ResultsDisplay';

function App() {
  const [backtestResult, setBacktestResult] = useState(null);

  const handleBacktestComplete = (data) => {
    console.log('Backtest completed:', data);
    setBacktestResult(data.backtest);
  };

  return (
    <div className="App">
      <header style={{
        backgroundColor: '#1f2937',
        color: 'white',
        padding: '20px',
        textAlign: 'center',
        marginBottom: '30px'
      }}>
        <h1 style={{ margin: 0, fontSize: '32px' }}>📈 Trading Backtester</h1>
        <p style={{ margin: '10px 0 0 0', color: '#9ca3af' }}>
          Test your algorithmic trading strategies
        </p>
      </header>

      <main>
        <BacktestForm onBacktestComplete={handleBacktestComplete} />
        
        {backtestResult && (
          <ResultsDisplay backtest={backtestResult} />
        )}
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '20px',
        color: '#6b7280',
        marginTop: '50px',
        borderTop: '1px solid #e5e7eb'
      }}>
        <p>Built with React + Flask + PostgreSQL</p>
      </footer>
    </div>
  );
}

export default App;