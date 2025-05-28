import React from 'react';
import './OverviewTab.css';

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
      <h2>{selectedYear} F1 Season Overview</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.drivers.length}</div>
          <div className="stat-label">Total Drivers</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number">{stats.sessions.length}</div>
          <div className="stat-label">Sessions</div>
        </div>
        
        {stats.sessions[0] && (
          <div className="stat-card latest-session">
            <div className="stat-label">Latest Session</div>
            <div className="stat-content">
              <div className="session-name">
                🏁 {stats.sessions[0].name}
              </div>
              <div className="session-location">
                📍 {stats.sessions[0].location}
              </div>
              <div className="session-date">
                📅 {stats.sessions[0].date ? 
                  new Date(stats.sessions[0].date).toLocaleDateString('en-US', {
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
    </div>
  );
};

export default OverviewTab; 