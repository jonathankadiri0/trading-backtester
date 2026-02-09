import React, { useEffect, useState } from 'react';
import axios from 'axios';
import PerformanceChart from './PerformanceChart';
import TradeTimeline from './TradeTimeline';

function ResultsDisplay({ backtest }) {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchTrades = async () => {
      if (!backtest || !backtest.id) return;
      
      setLoading(true);
      try {
        const response = await axios.get(`http://localhost:5000/api/backtests/${backtest.id}`);
        setTrades(response.data.trades);
      } catch (error) {
        console.error('Error fetching trades:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
  }, [backtest]);

  if (!backtest) {
    return null;
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getReturnColor = (value) => {
    return value >= 0 ? '#10b981' : '#ef4444';
  };

  const profit = backtest.final_value - backtest.initial_capital;

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '30px auto', 
      padding: '0 20px',
      animation: 'fadeIn 0.5s ease-in'
    }}>
      {/* Success Banner */}
      <div style={{
        backgroundColor: '#d1fae5',
        border: '1px solid #10b981',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '30px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <span style={{ fontSize: '24px' }}>✅</span>
        <div>
          <h3 style={{ margin: 0, color: '#065f46', fontSize: '18px' }}>
            Backtest Completed Successfully
          </h3>
          <p style={{ margin: '4px 0 0 0', color: '#047857', fontSize: '14px' }}>
            {backtest.ticker} • {backtest.start_date} to {backtest.end_date}
          </p>
        </div>
      </div>

      {/* Main Metrics Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', 
        gap: '20px',
        marginBottom: '30px'
      }}>
        
        {/* Profit Card */}
        <div style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          boxShadow: '0 10px 25px rgba(102, 126, 234, 0.3)',
          transform: 'translateY(0)',
          transition: 'transform 0.3s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>
            Total Profit/Loss
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '4px' }}>
            {formatCurrency(profit)}
          </div>
          <div style={{ fontSize: '18px', opacity: 0.9 }}>
            {formatPercent(backtest.total_return)}
          </div>
        </div>

        {/* Portfolio Value Card */}
        <div style={{ 
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          boxShadow: '0 10px 25px rgba(240, 147, 251, 0.3)',
          transform: 'translateY(0)',
          transition: 'transform 0.3s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>
            Final Portfolio Value
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '4px' }}>
            {formatCurrency(backtest.final_value)}
          </div>
          <div style={{ fontSize: '14px', opacity: 0.8 }}>
            from {formatCurrency(backtest.initial_capital)}
          </div>
        </div>

        {/* Sharpe Ratio Card */}
        <div style={{ 
          background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          boxShadow: '0 10px 25px rgba(79, 172, 254, 0.3)',
          transform: 'translateY(0)',
          transition: 'transform 0.3s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>
            Sharpe Ratio
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '4px' }}>
            {backtest.sharpe_ratio.toFixed(2)}
          </div>
          <div style={{ fontSize: '14px', opacity: 0.8 }}>
            {backtest.sharpe_ratio > 1 ? 'Excellent 🎯' : backtest.sharpe_ratio > 0.5 ? 'Good ✓' : 'Poor'}
          </div>
        </div>

        {/* Max Drawdown Card */}
        <div style={{ 
          background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          boxShadow: '0 10px 25px rgba(250, 112, 154, 0.3)',
          transform: 'translateY(0)',
          transition: 'transform 0.3s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>
            Max Drawdown
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '4px' }}>
            {formatPercent(backtest.max_drawdown)}
          </div>
          <div style={{ fontSize: '14px', opacity: 0.8 }}>
            {backtest.num_trades} trades executed
          </div>
        </div>

      </div>

      {/* Performance Chart */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        padding: '30px',
        marginBottom: '30px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
      }}>
        <PerformanceChart backtestId={backtest.id} />
      </div>

      {/* Trade Timeline and Details Side by Side */}
      <div style={{ 
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '30px',
        marginBottom: '30px'
      }}>
        
        {/* Trade Timeline */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '16px', 
          padding: '30px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>Loading trades...</div>
          ) : (
            <TradeTimeline trades={trades} />
          )}
        </div>

        {/* Details Table */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '16px', 
          padding: '30px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
        }}>
          <h3 style={{ marginBottom: '20px', color: '#1f2937' }}>Strategy Details</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              paddingBottom: '12px',
              borderBottom: '1px solid #e5e7eb'
            }}>
              <span style={{ color: '#6b7280', fontSize: '14px' }}>Stock Symbol</span>
              <span style={{ fontWeight: '600', fontSize: '16px', color: '#1f2937' }}>
                {backtest.ticker}
              </span>
            </div>

            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              paddingBottom: '12px',
              borderBottom: '1px solid #e5e7eb'
            }}>
              <span style={{ color: '#6b7280', fontSize: '14px' }}>Strategy</span>
              <span style={{ fontWeight: '600', fontSize: '14px', color: '#1f2937' }}>
                {backtest.strategy_name.replace(/_/g, ' ')}
              </span>
            </div>

            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              paddingBottom: '12px',
              borderBottom: '1px solid #e5e7eb'
            }}>
              <span style={{ color: '#6b7280', fontSize: '14px' }}>Test Period</span>
              <span style={{ fontWeight: '600', fontSize: '14px', color: '#1f2937' }}>
                {backtest.start_date} to {backtest.end_date}
              </span>
            </div>

            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              paddingBottom: '12px',
              borderBottom: '1px solid #e5e7eb'
            }}>
              <span style={{ color: '#6b7280', fontSize: '14px' }}>Total Trades</span>
              <span style={{ fontWeight: '600', fontSize: '16px', color: '#1f2937' }}>
                {backtest.num_trades}
              </span>
            </div>

            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              paddingBottom: '12px',
              borderBottom: '1px solid #e5e7eb'
            }}>
              <span style={{ color: '#6b7280', fontSize: '14px' }}>Win Rate</span>
              <span style={{ fontWeight: '600', fontSize: '16px', color: '#10b981' }}>
                {profit > 0 ? '100%' : '0%'}
              </span>
            </div>

            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between'
            }}>
              <span style={{ color: '#6b7280', fontSize: '14px' }}>Status</span>
              <span style={{ 
                fontWeight: '600', 
                fontSize: '14px', 
                color: '#10b981',
                backgroundColor: '#d1fae5',
                padding: '4px 12px',
                borderRadius: '12px'
              }}>
                {backtest.status}
              </span>
            </div>

          </div>
        </div>

      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

export default ResultsDisplay;