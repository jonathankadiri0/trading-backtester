import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import axios from 'axios';

function PerformanceChart({ backtestId }) {
  const [chartData, setChartData] = useState([]);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/backtests/${backtestId}`);
        const data = response.data;

        // Format portfolio history for chart
        const formatted = data.portfolio_history.map(item => ({
          date: item.date,
          portfolio: item.portfolio_value,
          stockPrice: item.stock_price,
        }));

        setChartData(formatted);
        setTrades(data.trades);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching chart data:', error);
        setLoading(false);
      }
    };

    if (backtestId) {
      fetchData();
    }
  }, [backtestId]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading chart...</div>;
  }

  if (chartData.length === 0) {
    return null;
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '12px',
          border: '1px solid #e5e7eb',
          borderRadius: '6px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: '600', color: '#1f2937' }}>
            {payload[0].payload.date}
          </p>
          <p style={{ margin: '4px 0', color: '#3b82f6' }}>
            Portfolio: ${payload[0].value.toFixed(2)}
          </p>
          <p style={{ margin: '4px 0', color: '#10b981' }}>
            Stock Price: ${payload[1].value.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ margin: '30px 0' }}>
      <h3 style={{ marginBottom: '20px', color: '#1f2937' }}>Portfolio Performance</h3>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${value.toFixed(0)}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          <Line 
            type="monotone" 
            dataKey="portfolio" 
            stroke="#3b82f6" 
            strokeWidth={2}
            name="Portfolio Value"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="stockPrice" 
            stroke="#10b981" 
            strokeWidth={2}
            name="Stock Price"
            dot={false}
            strokeDasharray="5 5"
          />
          
          {/* Mark buy/sell points */}
          {trades.map((trade, idx) => (
            <ReferenceLine
              key={idx}
              x={trade.date}
              stroke={trade.trade_type === 'BUY' ? '#10b981' : '#ef4444'}
              strokeWidth={2}
              label={{
                value: trade.trade_type,
                position: 'top',
                fill: trade.trade_type === 'BUY' ? '#10b981' : '#ef4444',
                fontSize: 12
              }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PerformanceChart;