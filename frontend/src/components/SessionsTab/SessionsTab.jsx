import React from 'react';
import './SessionsTab.css';

const SessionsTab = ({ sessions, selectedYear }) => {
  if (!sessions.length) {
    return (
      <div className="no-data">
        <h2>🏁 No Sessions Found</h2>
        <p>No session data available for {selectedYear}. Try syncing the data first.</p>
      </div>
    );
  }

  const getSessionTypeColor = (sessionType) => {
    switch (sessionType?.toLowerCase()) {
      case 'race':
        return '#dc143c';
      case 'qualifying':
        return '#ffd700';
      case 'practice':
        return '#90EE90';
      case 'sprint':
        return '#ff6347';
      default:
        return '#87ceeb';
    }
  };

  const formatSessionType = (sessionType) => {
    if (!sessionType) return 'Unknown';
    return sessionType.charAt(0).toUpperCase() + sessionType.slice(1).toLowerCase();
  };

  // Group sessions by location/weekend
  const groupedSessions = sessions.reduce((acc, session) => {
    const key = `${session.location}-${session.country_name}`;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(session);
    return acc;
  }, {});

  return (
    <div className="sessions-section">
      <h2>🏁 {selectedYear} F1 Sessions</h2>
      
      <div className="sessions-overview">
        <p>Total Sessions: <strong>{sessions.length}</strong></p>
        <p>Race Weekends: <strong>{Object.keys(groupedSessions).length}</strong></p>
      </div>

      <div className="sessions-list">
        {Object.entries(groupedSessions).map(([location, locationSessions]) => (
          <div key={location} className="weekend-group">
            <div className="weekend-header">
              <h3>🏎️ {locationSessions[0].location}</h3>
              <p>📍 {locationSessions[0].country_name}</p>
              {locationSessions[0].circuit_short_name && (
                <p>🏁 {locationSessions[0].circuit_short_name}</p>
              )}
            </div>
            
            <div className="weekend-sessions">
              {locationSessions
                .sort((a, b) => new Date(a.date_start) - new Date(b.date_start))
                .map(session => (
                  <div 
                    key={session.id}
                    className="session-card"
                    style={{
                      backgroundColor: `${getSessionTypeColor(session.session_type)}22`,
                      borderLeft: `4px solid ${getSessionTypeColor(session.session_type)}`
                    }}
                  >
                    <div className="session-header">
                      <h4>{formatSessionType(session.session_type)}</h4>
                      <p>{new Date(session.date_start).toLocaleDateString()}</p>
                    </div>
                    
                    <div className="session-stats">
                      <div className="stat">
                        <span>Drivers:</span>
                        <strong>{session.driver_count || 0}</strong>
                      </div>
                      <div className="stat">
                        <span>Laps:</span>
                        <strong>{session.lap_count || 0}</strong>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SessionsTab; 