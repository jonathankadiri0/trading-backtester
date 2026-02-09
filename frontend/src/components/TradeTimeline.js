import React from 'react';

function TradeTimeline({ trades }) {
  if (!trades || trades.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
        No trades executed yet
      </div>
    );
  }

  return (
    <div style={{ margin: '30px 0' }}>
      <h3 style={{ marginBottom: '20px', color: '#1f2937' }}>Trade History</h3>
      
      <div style={{ position: 'relative', paddingLeft: '30px' }}>
        {/* Timeline line */}
        <div style={{
          position: 'absolute',
          left: '8px',
          top: '0',
          bottom: '0',
          width: '2px',
          backgroundColor: '#e5e7eb'
        }} />
        
        {trades.map((trade, index) => {
          const isBuy = trade.trade_type === 'BUY';
          const color = isBuy ? '#10b981' : '#ef4444';
          const bgColor = isBuy ? '#d1fae5' : '#fee2e2';
          
          return (
            <div key={index} style={{ 
              position: 'relative', 
              marginBottom: '24px',
              paddingLeft: '20px'
            }}>
              {/* Timeline dot */}
              <div style={{
                position: 'absolute',
                left: '-22px',
                top: '4px',
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                backgroundColor: color,
                border: '3px solid white',
                boxShadow: '0 0 0 1px #e5e7eb'
              }} />
              
              {/* Trade card */}
              <div style={{
                backgroundColor: bgColor,
                borderLeft: `4px solid ${color}`,
                borderRadius: '6px',
                padding: '16px',
              }}>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '8px'
                }}>
                  <span style={{ 
                    fontWeight: '700',
                    fontSize: '16px',
                    color: color
                  }}>
                    {trade.trade_type}
                  </span>
                  <span style={{ 
                    fontSize: '14px',
                    color: '#6b7280'
                  }}>
                    {trade.date}
                  </span>
                </div>
                
                <div style={{ 
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '12px',
                  fontSize: '14px'
                }}>
                  {trade.price != null && (
                    <div>
                      <span style={{ color: '#6b7280' }}>Price: </span>
                      <span style={{ fontWeight: '600', color: '#1f2937' }}>
                        ${trade.price.toFixed(2)}
                      </span>
                    </div>
                  )}
                  
                  {trade.shares != null && (
                    <div>
                      <span style={{ color: '#6b7280' }}>Shares: </span>
                      <span style={{ fontWeight: '600', color: '#1f2937' }}>
                        {trade.shares.toFixed(2)}
                      </span>
                    </div>
                  )}
                  
                  {trade.capital != null && trade.capital > 0 && (
                    <div style={{ gridColumn: '1 / -1' }}>
                      <span style={{ color: '#6b7280' }}>Capital: </span>
                      <span style={{ fontWeight: '600', color: '#1f2937' }}>
                        ${trade.capital.toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TradeTimeline;