import React, { useState } from 'react';

const DriverDetails = ({ driver, sessions, selectedYear, onBack, onFetchSessionPositions }) => {
  const [selectedSession, setSelectedSession] = useState(null);
  const [sessionPositions, setSessionPositions] = useState(null);
  const [loadingPositions, setLoadingPositions] = useState(false);

  const handleSessionClick = async (session) => {
    if (selectedSession?.id === session.id) {
      setSelectedSession(null);
      setSessionPositions(null);
      return;
    }

    setSelectedSession(session);
    setLoadingPositions(true);
    
    try {
      const positions = await onFetchSessionPositions(session.id);
      setSessionPositions(positions);
    } catch (error) {
      console.error('Failed to fetch session positions:', error);
      setSessionPositions(null);
    } finally {
      setLoadingPositions(false);
    }
  };

  const getPositionColor = (position) => {
    if (!position) return 'transparent';
    if (position === 1) return '#FFD700'; // Gold
    if (position === 2) return '#C0C0C0'; // Silver
    if (position === 3) return '#CD7F32'; // Bronze
    if (position <= 10) return '#90EE90'; // Light green for points
    return '#FFB6C1'; // Light red for no points
  };

  return (
    <div className="driver-details">
      <button onClick={onBack} className="back-button">
        ← Back to Drivers
      </button>
      
      <div className="driver-header">
        <h2>🏎️ {driver.full_name}</h2>
        <div className="driver-meta">
          <span>#{driver.driver_number}</span>
          {driver.headshot_url && (
            <img 
              src={driver.headshot_url} 
              alt={driver.full_name}
              style={{
                width: '100px',
                height: '100px',
                borderRadius: '50%',
                objectFit: 'cover',
                margin: '1rem',
                border: '3px solid rgba(255, 255, 255, 0.3)'
              }}
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          )}
        </div>
      </div>

      <div className="sessions-table">
        <h3>📊 {selectedYear} Season Sessions</h3>
        <table>
          <thead>
            <tr>
              <th>Session</th>
              <th>Location</th>
              <th>Date</th>
              <th>Position</th>
              <th>Points</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map(session => (
              <React.Fragment key={session.id}>
                <tr 
                  className={selectedSession?.id === session.id ? 'selected' : ''}
                  style={{ cursor: 'pointer' }}
                >
                  <td>{session.session_name}</td>
                  <td>
                    {session.location}
                    {session.circuit_short_name && (
                      <small> ({session.circuit_short_name})</small>
                    )}
                  </td>
                  <td>
                    {session.date_start ? 
                      new Date(session.date_start).toLocaleDateString() : 
                      'TBD'
                    }
                  </td>
                  <td>
                    <span 
                      className="position-badge"
                      style={{
                        backgroundColor: getPositionColor(session.final_position),
                        color: session.final_position && session.final_position <= 3 ? '#000' : '#fff',
                        padding: '0.3rem 0.6rem',
                        borderRadius: '15px',
                        fontWeight: 'bold'
                      }}
                    >
                      {session.final_position || 'N/A'}
                    </span>
                  </td>
                  <td>{session.points || 0}</td>
                  <td>
                    <button 
                      onClick={() => handleSessionClick(session)}
                      className="details-button"
                      style={{
                        background: 'rgba(255, 215, 0, 0.2)',
                        border: '1px solid rgba(255, 215, 0, 0.5)',
                        color: '#ffd700',
                        padding: '0.3rem 0.8rem',
                        borderRadius: '15px',
                        cursor: 'pointer',
                        fontSize: '0.8rem'
                      }}
                    >
                      {selectedSession?.id === session.id ? 'Hide' : 'Show'} Progress
                    </button>
                  </td>
                </tr>
                
                {selectedSession?.id === session.id && (
                  <tr>
                    <td colSpan="6" style={{ padding: '1rem', background: 'rgba(255, 215, 0, 0.1)' }}>
                      {loadingPositions ? (
                        <div>Loading position data...</div>
                      ) : sessionPositions && sessionPositions.positions ? (
                        <div className="position-timeline">
                          <h4>📈 Position Timeline</h4>
                          <div className="positions-chart">
                            {sessionPositions.positions.map((pos, index) => (
                              <div key={index} className="position-point">
                                <small>{new Date(pos.date).toLocaleTimeString()}</small>
                                <strong>P{pos.position}</strong>
                              </div>
                            ))}
                          </div>
                          <p>
                            <strong>Final Position:</strong> {sessionPositions.driver_session.final_position || 'N/A'}
                          </p>
                        </div>
                      ) : (
                        <div>No position data available for this session.</div>
                      )}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DriverDetails;