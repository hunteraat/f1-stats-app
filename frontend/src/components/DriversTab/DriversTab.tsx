import React, { useState, useEffect } from 'react';
import './DriversTab.css';
import { Box, CircularProgress } from '@mui/material';
import { getCountryFlagUrl } from '../../utils/flags';
import { F1DataService } from '../../services/api/f1-data.service';
import DriverDetails from '../DriverDetails/DriverDetails';
import { Driver, DriverSession } from '../../types/models';
import { formatTeamColor } from '../../utils/util';

interface DriversTabProps {
  selectedYear: number;
}

const DriversTab: React.FC<DriversTabProps> = ({ selectedYear }) => {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null);
  const [driverSessions, setDriverSessions] = useState<DriverSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDrivers = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await F1DataService.getDrivers(selectedYear);
        setDrivers(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch drivers');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDrivers();
  }, [selectedYear]);

  const handleDriverClick = async (driver: Driver) => {
    setIsLoadingSessions(true);
    setError(null);
    try {
      const sessions = await F1DataService.getDriverSessions(driver.driver_number, selectedYear);
      setDriverSessions(sessions);
      setSelectedDriver(driver);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch driver sessions');
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const handleBack = () => {
    setSelectedDriver(null);
    setDriverSessions([]);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <div className="error-message">{error}</div>
      </Box>
    );
  }

  if (selectedDriver) {
    return (
      <DriverDetails
        selectedDriver={selectedDriver}
        driverSessions={driverSessions}
        isLoadingSessions={isLoadingSessions}
        onBack={handleBack}
        backText="Back to Drivers"
      />
    );
  }

  return (
    <div className="drivers-container">
      <h1 className="overview-header">{selectedYear} Season Drivers</h1>
      <div className="drivers-grid">
        {drivers.map((driver) => (
          <div
            key={driver.driver_number}
            className="driver-card"
            onClick={() => handleDriverClick(driver)}
            style={{ backgroundColor: formatTeamColor(driver.team_colour) }}
          >
            <div className="driver-background" style={{
              backgroundImage: `url(${driver.headshot_url})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }} />
            
            <div className="driver-top-stats">
              <div className="points">{driver.points} pts</div>
              <div className="position">P{driver.position}</div>
            </div>

            <div className="driver-info-container">
              <div className="driver-info">
                <div className="driver-name">
                  {driver.full_name} <span className="driver-number">#{driver.driver_number}</span>
                </div>
                <div className="team-name">{driver.team_name}</div>
              </div>

              <div className="driver-stats">
                <div className="stat-circle">
                  <span className="stat-value" title="Wins">🏆{driver.wins}</span>
                </div>
                <div className="stat-circle">
                  <span className="stat-value" title="Podiums">🥈{driver.podiums}</span>
                </div>
                <div className="stat-circle">
                  <span className="stat-value" title="Fastest Laps">⚡{driver.fastest_laps}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DriversTab; 