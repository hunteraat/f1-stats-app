import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [drivers, setDrivers] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncLoading, setSyncLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [driverSessions, setDriverSessions] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch all data
  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [driversRes, sessionsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/drivers`),
        fetch(`${API_BASE_URL}/sessions`),
        fetch(`${API_BASE_URL}/stats/summary`)
      ]);

      if (!driversRes.ok || !sessionsRes.ok || !statsRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const [driversData, sessionsData, statsData] = await Promise.all([
        driversRes.json(),
        sessionsRes.json(),
        statsRes.json()
      ]);

      setDrivers(driversData);
      setSessions(sessionsData);
      setStats(statsData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Sync F1 data from OpenF1 API
  const syncF1Data = async () => {
    try {
      setSyncLoading(true);
      const response = await fetch(`${API_BASE_URL}/sync-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ year: 2024 })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to sync data');
      }

      // Refresh data after sync
      await fetchData();
      
      alert(`✅ ${result.message}\n📊 Processed ${result.drivers_processed} drivers and ${result.sessions_processed} sessions`);
    } catch (err) {
      setError(`Sync failed: ${err.message}`);
      alert(`❌ Sync failed: ${err.message}`);
    } finally {
      setSyncLoading(false);
    }
  };

  // Fetch driver sessions
  const fetchDriverSessions = async (driverId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/drivers/${driverId}/sessions`);
      if (!response.ok) {
        throw new Error('Failed to fetch driver sessions');
      }
      const data = await response.json();
      setDriverSessions(data.sessions);
      setSelectedDriver(data.driver);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">🏎️ Loading F1 data...</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏁 F1 Driver Statistics</h1>
        <p>Formula 1 driver data powered by OpenF1 API</p>
        <div className="header-actions">
          <button 
            onClick={syncF1Data} 
            disabled={syncLoading}
            className="sync-button"
          >
            {syncLoading ? '🔄 Syncing...' : '📥 Sync Latest Data'}
          </button>
        </div>
      </header>

      <nav className="tab-navigation">
        <button 
          className={activeTab === 'overview' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={activeTab === 'drivers' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('drivers')}
        >
          🏎️ Drivers
        </button>
        <button 
          className={activeTab === 'sessions' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('sessions')}
        >
          🏁 Sessions
        </button>
      </nav>

      <main className="main-content">
        {error && (
          <div className="error-message">
            ❌ Error: {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {activeTab === 'overview' && (
          <OverviewTab stats={stats} />
        )}

        {activeTab === 'drivers' && (
          <DriversTab 
            drivers={drivers} 
            selectedDriver={selectedDriver}
            driverSessions={driverSessions}
            onDriverSelect={fetchDriverSessions}
            onBackToDrivers={() => setSelectedDriver(null)}
          />
        )}

        {activeTab === 'sessions' && (
          <SessionsTab sessions={sessions} />
        )}
      </main>
    </div>
  );
}

// Overview Tab Component
function OverviewTab({ stats }) {
  if (!stats) {
    return <div className="loading">Loading statistics...</div>;
  }

  return (
    <div className="overview-section">
      <h2>📈 Statistics Overview</h2>
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
          <div className="stat-label">Total Sessions</div>
        </div>
        <div className="stat-card latest-session">
          <div className="stat-content">
            <div className="stat-label">Latest Session</div>
            {stats.latest_session ? (
              <>
                <div className="session-name">{stats.latest_session.name}</div>
                <div className="session-location">📍 {stats.latest_session.location}</div>
                <div className="session-date">
                  📅 {new Date(stats.latest_session.date).toLocaleDateString()}
                </div>
              </>
            ) : (
              <div className="no-data">No sessions available</div>
            )}
          </div>
        </div>
      </div>
      
      {stats.last_sync && (
        <div className="sync-info">
          <p>🔄 Last data sync: {new Date(stats.last_sync).toLocaleString()}</p>
        </div>
      )}
    </div>
  );
}

// Drivers Tab Component
function DriversTab({ drivers, selectedDriver, driverSessions, onDriverSelect, onBackToDrivers }) {
  if (selectedDriver) {
    return (
      <div className="driver-details">
        <button onClick={onBackToDrivers} className="back-button">
          ← Back to Drivers
        </button>
        <div className="driver-header">
          <div className="driver-info">
            <h2>🏎️ {selectedDriver.full_name}</h2>
            <p>Driver #{selectedDriver.driver_number}</p>
          </div>
        </div>
        
        <h3>🏁 Session History ({driverSessions.length})</h3>
        {driverSessions.length === 0 ? (
          <p className="no-data">No session data available for this driver.</p>
        ) : (
          <div className="sessions-table">
            <table>
              <thead>
                <tr>
                  <th>Session</th>
                  <th>Location</th>
                  <th>Date</th>
                  <th>Position</th>
                  <th>Points</th>
                </tr>
              </thead>
              <tbody>
                {driverSessions.map((session, index) => (
                  <tr key={index}>
                    <td>{session.session_name}</td>
                    <td>
                      {session.location && (
                        <>
                          📍 {session.circuit_short_name || session.location}
                          <br />
                          <small>{session.country_name}</small>
                        </>
                      )}
                    </td>
                    <td>
                      {session.date_start && 
                        new Date(session.date_start).toLocaleDateString()
                      }
                    </td>
                    <td>{session.position || '-'}</td>
                    <td>{session.points || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="drivers-section">
      <h2>🏎️ F1 Drivers ({drivers.length})</h2>
      {drivers.length === 0 ? (
        <div className="no-data">
          <p>No drivers found. Click "Sync Latest Data" to fetch F1 driver information.</p>
        </div>
      ) : (
        <div className="drivers-grid">
          {drivers.map(driver => (
            <div 
              key={driver.id} 
              className="driver-card"
              onClick={() => onDriverSelect(driver.id)}
            >
              <div className="driver-number">#{driver.driver_number}</div>
              <div className="driver-info">
                <h3>{driver.full_name}</h3>
                <p className="team-name">{driver.team_name || 'No team'}</p>
                <p className="country">{driver.country_code && `🏁 ${driver.country_code}`}</p>
                <div className="driver-stats">
                  <span className="session-count">
                    📊 {driver.session_count} sessions
                  </span>
                </div>
              </div>
              {driver.team_colour && (
                <div 
                  className="team-color" 
                  style={{ backgroundColor: driver.team_colour }}
                ></div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Sessions Tab Component
function SessionsTab({ sessions }) {
  return (
    <div className="sessions-section">
      <h2>🏁 F1 Sessions ({sessions.length})</h2>
      {sessions.length === 0 ? (
        <div className="no-data">
          <p>No sessions found. Click "Sync Latest Data" to fetch F1 session information.</p>
        </div>
      ) : (
        <div className="sessions-list">
          {sessions.map(session => (
            <div key={session.id} className="session-card">
              <div className="session-header">
                <h3>{session.session_name}</h3>
                <span className="session-type">{session.session_type}</span>
              </div>
              <div className="session-details">
                <p className="location">
                  📍 {session.circuit_short_name || session.location}
                  {session.country_name && `, ${session.country_name}`}
                </p>
                <p className="date">
                  📅 {session.date_start && new Date(session.date_start).toLocaleString()}
                </p>
                <p className="year">🏆 {session.year}</p>
                <p className="drivers">👥 {session.driver_count} drivers</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;