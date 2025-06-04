import React, { useState, useEffect } from 'react';
import './ConstructorsTab.css';
import { Box, CircularProgress } from '@mui/material';
import { getCountryFlagUrl } from '../../utils/flags';
import { F1DataService } from '../../services/api/f1-data.service';
import DriverDetails from '../DriverDetails/DriverDetails';
import { Driver, Constructor, DriverSession } from '../../types/models';
import { formatTeamColor } from '../../utils/util';

interface ConstructorsTabProps {
  selectedYear: number;
}

const formatDriverName = (name: string): string => {
  if (!name) return 'Unknown Driver';
  const parts = name.split(' ');
  if (parts.length === 1) return name;
  const lastName = parts.pop();
  const initials = parts.map((part: string) => part[0]).join('. ');
  return `${initials}. ${lastName}`;
};

const getDriverImageUrl = (url: string | null): string | null => {
  if (!url) return null;
  return url;
};

const ConstructorsTab: React.FC<ConstructorsTabProps> = ({ selectedYear }) => {
  const [constructors, setConstructors] = useState<Constructor[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null);
  const [driverSessions, setDriverSessions] = useState<DriverSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [constructorsResponse, driversResponse] = await Promise.all([
          F1DataService.getConstructors(selectedYear),
          F1DataService.getDrivers(selectedYear)
        ]);
        setConstructors(constructorsResponse);
        setDrivers(driversResponse);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to fetch constructor data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [selectedYear]);

  const handleDriverSelect = async (driver: Driver) => {
    setIsLoadingSessions(true);
    setError(null);
    try {
      const sessions = await F1DataService.getDriverSessions(driver.driver_number, selectedYear);
      setDriverSessions(sessions);
      setSelectedDriver(driver);
    } catch (error) {
      console.error('Error fetching driver sessions:', error);
      setError('Failed to fetch driver sessions');
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const handleBackToConstructors = () => {
    setSelectedDriver(null);
    setDriverSessions([]);
  };

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

  if (selectedDriver) {
    return (
      <DriverDetails
        selectedDriver={selectedDriver}
        driverSessions={driverSessions}
        isLoadingSessions={isLoadingSessions}
        onBack={handleBackToConstructors}
        backText="Back to Constructors"
      />
    );
  }

  // Group drivers by team
  const driversByTeam = drivers.reduce((teams, driver) => {
    const teamName = driver.team_name || 'Unknown Team';
    const constructor = constructors.find(c => c.team_name === teamName);
    
    if (!teams[teamName]) {
      teams[teamName] = {
        drivers: [],
        teamColor: constructor?.team_colour || '#333333',
        points: constructor?.points || 0,
        position: constructor?.position || 0,
        wins: constructor?.wins || 0,
        podiums: constructor?.podiums || 0,
        fastest_laps: constructor?.fastest_laps || 0,
        races: constructor?.races || 0
      };
    }
    teams[teamName].drivers.push(driver);
    return teams;
  }, {} as Record<string, { 
    drivers: Driver[]; 
    teamColor: string; 
    points: number; 
    position: number;
    wins: number;
    podiums: number;
    fastest_laps: number;
    races: number;
  }>);

  return (
    <div className="constructors-container">
      <h1 className="overview-header">{selectedYear} Season Constructors</h1>
      <div className="constructors-grid">
        {Object.entries(driversByTeam)
          .sort(([, a], [, b]) => a.position - b.position)
          .map(([teamName, team]) => (
            <div
              key={teamName}
              className="constructor-card"
              style={{ backgroundColor: formatTeamColor(team.teamColor) }}
            >
              <div className="constructor-header">
                <h3>{teamName}</h3>
                <div className="constructor-position">
                  P{team.position}
                </div>
              </div>
              <div className="constructor-stats">
                <span className="constructor-stat" title="Points">Points: {team.points}</span>
                <span className="constructor-stat" title="Podiums">🥈 {team.podiums}</span>
                <span className="constructor-stat" title="Wins">🏆 {team.wins}</span>
                <span className="constructor-stat" title="Fastest Laps">⚡ {team.fastest_laps}</span>
                <span className="constructor-stat" title="Races">🏎️ {team.races}</span>
              </div>
              <div className="constructor-drivers">
                {team.drivers.map(driver => (
                  <div
                    key={driver.driver_number}
                    className="constructor-driver-info"
                    onClick={() => handleDriverSelect(driver)}
                  >
                    <div className="constructor-driver-header">
                      <span className="constructor-driver-name">{driver.full_name}</span>
                      <span className="constructor-driver-number">#{driver.driver_number}</span>
                    </div>
                    <div className="constructor-driver-stats">
                      <span className="constructor-driver-stat" title="Points">Points: {driver.points}</span>
                      <span className="constructor-driver-stat" title="Podiums">🥈 {driver.podiums}</span>
                      <span className="constructor-driver-stat" title="Wins">🏆 {driver.wins}</span>
                      <span className="constructor-driver-stat" title="Fastest Laps">⚡ {driver.fastest_laps}</span>
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

export default ConstructorsTab; 