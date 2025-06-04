import React from 'react';
import { Box, Button, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { Driver, DriverSession } from '../../types/models';
import './DriverDetails.css';
import { getCountryFlagUrl } from '../../utils/flags';

interface DriverDetailsProps {
  selectedDriver: Driver;
  driverSessions: DriverSession[];
  isLoadingSessions: boolean;
  onBack: () => void;
  backText: string;
}

const DriverDetails: React.FC<DriverDetailsProps> = ({
  selectedDriver,
  driverSessions,
  isLoadingSessions,
  onBack,
  backText
}) => {
  const getRowClassName = (session: DriverSession) => {
    if (session.final_position === 1 && session.session_type === 'Race') return 'win-row';
    if (session.final_position !== null && session.final_position <= 3 && session.session_type === 'Race') return 'podium-row';
    return '';
  };

  return (
    <div className="driver-details">
      <Button variant="outlined" onClick={onBack} className="back-button">
        {backText}
      </Button>
      
      <div className="driver-details-header">
        <h1>
          {selectedDriver.full_name}
          <img className="country-flag" src={getCountryFlagUrl(selectedDriver.country_code)} alt={selectedDriver.country_code} />
        </h1>
        <h2>Driver for {selectedDriver.team_name}</h2>
      </div>

      <div className="driver-summary">
        <div className="summary-item">
          <span className="label">Driver Number</span>
          <span className="value">#{selectedDriver.driver_number}</span>
        </div>
        <div className="summary-item">
          <span className="label">Total Points</span>
          <span className="value">{selectedDriver.points}</span>
        </div>
        <div className="summary-item">
          <span className="label">Wins</span>
          <span className="value">{selectedDriver.wins}</span>
        </div>
        <div className="summary-item">
          <span className="label">Podiums</span>
          <span className="value">{selectedDriver.podiums}</span>
        </div>
        <div className="summary-item">
          <span className="label">Fastest Laps</span>
          <span className="value">{selectedDriver.fastest_laps}</span>
        </div>
        <div className="summary-item">
          <span className="label">Total Races</span>
          <span className="value">{selectedDriver.races}</span>
        </div>
      </div>

      <div className="sessions-section">
        <h3>Race Sessions</h3>
        {isLoadingSessions ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper} className="sessions-table">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Session Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Position</TableCell>
                  <TableCell>Points</TableCell>
                  <TableCell>Fastest Lap</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {driverSessions.map((session) => (
                  <TableRow 
                    key={session.full_name + session.session_name + session.location + session.date_start}
                    className={getRowClassName(session)}
                  >
                    <TableCell>{session.session_name}</TableCell>
                    <TableCell>{session.session_type}</TableCell>
                    <TableCell>{session.location}</TableCell>
                    <TableCell>
                      {session.date_start && new Date(session.date_start).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{session.final_position}</TableCell>
                    <TableCell>{session.points}</TableCell>
                    <TableCell>{session.fastest_lap ? 'Yes' : 'No'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </div>
    </div>
  );
};

export default DriverDetails; 