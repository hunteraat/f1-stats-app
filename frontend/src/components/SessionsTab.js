import React from 'react';

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
                  <div key={session.id} className="session-card">
                    <div className="session-header">
                      <h4>{session.session_name}</h4>
                      <span 
                        className="session-type"
                        style={{ 
                          backgroundColor: getSessionTypeColor(session.session_type),
                          color: session.session_type?.toLowerCase() === 'qualifying' ? '#000' : '#fff'
                        }}
                      >
                        {formatSessionType(session.session_type)}
                      </span>
                    </div>
                    
                    <div className="session-details">
                      <p>
                        <strong>📅 Date:</strong> {' '}
                        {session.date_start ? 
                          new Date(session.date_start).toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          }) : 
                          'TBD'
                        }
                      </p>
                      
                      {session.date_start && (
                        <p>
                          <strong>🕐 Time:</strong> {' '}
                          {new Date(session.date_start).toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      )}
                      
                      <p>
                        <strong>👥 Drivers:</strong> {session.driver_count || 0}
                      </p>
                      
                      <small>
                        Session Key: {session.session_key}
                      </small>
                    </div>
                  </div>
                ))
              }
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SessionsTab;