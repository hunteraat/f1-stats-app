import React, { useState, useEffect } from 'react';
import { Box, CircularProgress } from '@mui/material';

import { F1DataService } from '../../services/api/f1-data.service';
import './SessionsTab.css';

interface SessionsTabProps {
  selectedYear: number;
}

interface Session {
  id: number;
  session_key: string;
  session_name: string;
  date_start: string | null;
  location: string;
  country_name: string;
  circuit_short_name: string;
  year: number;
  session_type: string;
  driver_count: number;
  lap_count?: number;
}

const SessionsTab: React.FC<SessionsTabProps> = ({ selectedYear }) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await F1DataService.getSessions(selectedYear);
        setSessions(response);
      } catch (error) {
        setError('Failed to fetch sessions');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessions();
  }, [selectedYear]);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <div className="error-message">{error}</div>
      </Box>
    );
  }

  return (
    <div className="sessions-container">
      <div className="sessions-grid">
        {sessions.map(session => (
          <div key={session.id} className="session-card">
            <div className="session-header">
              <h3>{session.session_name}</h3>
              <span className="session-type">{session.session_type}</span>
            </div>
            <div className="session-info">
              <div className="location">
                <span className="label">Location:</span>
                <span className="value">{session.location}</span>
              </div>
              {session.date_start && (
                <div className="date">
                  <span className="label">Date:</span>
                  <span className="value">
                    {new Date(session.date_start).toLocaleDateString()}
                  </span>
                </div>
              )}
              <div className="stats">
                <div className="stat">
                  <span className="label">Drivers:</span>
                  <span className="value">{session.driver_count}</span>
                </div>
                {session.lap_count !== undefined && (
                  <div className="stat">
                    <span className="label">Laps:</span>
                    <span className="value">{session.lap_count}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SessionsTab;
