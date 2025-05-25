import React from 'react';

const OverviewTab = ({ stats, selectedYear }) => {
  if (!stats) {
    return (
      <div className="overview-section">
        <div className="loading">Loading statistics...</div>
      </div>
    );
  }

  return (
    <div className="overview-section">
      <h2>📊 {selectedYear} F1 Season Overview</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.total_drivers}</div>
          <div className="stat-label">Total Drivers</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number">{stats.active_drivers}</div>
          <div className="stat-label">Active Drivers</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number">{stats.total_sessions}</div>
          <div className="stat-label">Sessions</div>
        </div>
        
        {stats.latest_session && (
          <div className="stat-card latest-session">
            <div className="stat-content">
              <div className="session-name">
                🏁 {stats.latest_session.name}
              </div>
              <div className="session-location">
                📍 {stats.latest_session.location}
              </div>
              <div className="session-date">
                📅 {stats.latest_session.date ? 
                  new Date(stats.latest_session.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  }) : 'Date TBD'
                }
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="sync-info">
        <p>💡 Use the sync button to refresh data from OpenF1 API</p>
        <p>🏎️ Navigate to Drivers tab to explore individual driver statistics</p>
        <p>🏁 Check Sessions tab for race weekend details</p>
      </div>
    </div>
  );
};

export default OverviewTab;