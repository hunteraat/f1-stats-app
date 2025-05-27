import React from 'react';

// Convert 3-letter country codes to 2-letter codes for flags
const countryCodeMapping = {
  'USA': 'US',
  'NED': 'NL',
  'MEX': 'MX',
  'FRA': 'FR',
  'ARG': 'AR',
  'CAN': 'CA',
  'GBR': 'GB',
  'AUS': 'AU',
  'ESP': 'ES',
  'MON': 'MC',
  'CHN': 'CN',
  'THA': 'TH',
  'DEU': 'DE',
  'FIN': 'FI',
  'JPN': 'JP',
  'DNK': 'DK',
  'ITA': 'IT',
  'BRA': 'BR',
  'AUT': 'AT',
  'RUS': 'RU',
  'HUN': 'HU',
  'BEL': 'BE',
  'MCO': 'MC',
  'ISR': 'IL',
  'ROU': 'RO',
  'TUR': 'TR',
  'IND': 'IN',
  'KOR': 'KR',
  'SUI': 'CH',  
  'MAL': 'MY',
  'SAU': 'SA',
  'QAT': 'QA',
  'HKG': 'HK',
  'CRO': 'HR',
  'CIV': 'CI',
  'GER': 'DE',
  'POL': 'PL',
  'TUN': 'TN',
  'BUL': 'BG',
  'NOR': 'NO',
  'DEN': 'DK',
  'SVK': 'SK',
  'BHR': 'BH',
  'KAZ': 'KZ',
  'MOR': 'MA',
  
  // Add more mappings as needed
};

// Function to get flag URL from country code
const getCountryFlagUrl = (countryCode) => {
  if (!countryCode) return null;
  const twoLetterCode = (countryCodeMapping[countryCode] || countryCode).toLowerCase();
  return `https://flagcdn.com/w40/${twoLetterCode}.png`;
};

// Function to ensure color is in proper hex format
const formatTeamColor = (color) => {
  if (!color) return '#333333';
  // Remove any # prefix
  const cleanColor = color.replace('#', '');
  // Ensure it's a 6-digit hex
  if (cleanColor.length === 6) {
    return `#${cleanColor}`;
  }
  return '#333333';
};

// Function to properly capitalize a name
const formatDriverName = (name) => {
  if (!name) return '';
  return name.split(' ')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
};

const DriversTab = ({ 
  drivers, 
  selectedDriver, 
  driverSessions, 
  selectedYear,
  onDriverSelect, 
  onBackToDrivers,
  onFetchSessionPositions 
}) => {
  // Group drivers by team
  const driversByTeam = drivers.reduce((teams, driver) => {
    const teamName = driver.team_name || 'Unknown Team';
    const formattedColor = formatTeamColor(driver.team_colour);
    
    if (!teams[teamName]) {
      teams[teamName] = {
        drivers: [],
        teamColor: formattedColor,
        validTeamColor: formattedColor !== '#333333' ? formattedColor : null,
        teamPoints: driver.team_points || 0,
        constructorPosition: driver.constructor_position || 0
      };
    } else if (!teams[teamName].validTeamColor && formattedColor !== '#333333') {
      teams[teamName].validTeamColor = formattedColor;
      teams[teamName].teamColor = formattedColor;
    }
    teams[teamName].drivers.push(driver);
    return teams;
  }, {});

  if (selectedDriver) {
    return (
      <div className="driver-details">
        <button onClick={onBackToDrivers} className="back-button">
          ← Back to Drivers
        </button>
        
        <div className="driver-header">
          <h2>{formatDriverName(selectedDriver.full_name)}</h2>
          <p>Driver #{selectedDriver.driver_number}</p>
        </div>
        
        <div className="sessions-table">
          <table>
            <thead>
              <tr>
                <th className="left-spacing">Session</th>
                <th className="left-spacing">Location</th>
                <th className="left-spacing">Date</th>
                <th>Position</th>
                <th>Points</th>
                <th>Fastest Lap</th>
              </tr>
            </thead>
            <tbody>
              {driverSessions.map(session => (
                <tr key={session.id}>
                  <td className="left-spacing">{session.session_name}</td>
                  <td className="left-spacing">{session.location}</td>
                  <td className="left-spacing">{new Date(session.date_start).toLocaleDateString()}</td>
                  <td>{session.final_position || 'N/A'}</td>
                  <td>{session.points || 0}</td>
                  <td>{session.fastest_lap ? '✅' : '❌'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (!drivers.length) {
    return (
      <div className="drivers-section">
        <div className="no-data">
          No drivers found for {selectedYear}. Try syncing the data first.
        </div>
      </div>
    );
  }

  return (
    <div className="drivers-section">
      <h2>🏎️ Drivers ({selectedYear})</h2>
      
      <div className="teams-grid">
        {Object.entries(driversByTeam)
          .sort(([, teamA], [, teamB]) => teamA.constructorPosition - teamB.constructorPosition)
          .map(([teamName, team]) => (
          <div 
            key={teamName}
            className="team-container"
            style={{ 
              backgroundColor: team.validTeamColor ? `${team.validTeamColor}22` : '#33333322',
              borderLeft: `4px solid ${team.validTeamColor || '#333333'}`
            }}
          >
            <div className="team-header">
              <h3>{teamName}</h3>
              <div className="team-stats">
                <span className={`constructor-position 
                  ${team.constructorPosition === 1 ? 'champion' : ''}
                  ${team.constructorPosition > 1 && team.constructorPosition <= 3 ? 'podium' : ''}
                  ${team.constructorPosition > 3 && team.constructorPosition < 10 ? 'top-ten' : ''}
                  ${team.constructorPosition >= 10 ? 'below-ten' : ''}`}>
                  <span>Constructor Position: </span>
                  <span className="position-number">{team.constructorPosition}</span>
                </span>
                <span className="team-points">
                  {team.teamPoints} points
                </span>
              </div>
            </div>
            
            <div className="team-drivers">
              {team.drivers.map(driver => (
                <div 
                  key={driver.id} 
                  className="driver-card"
                  onClick={() => onDriverSelect(driver.id)}
                >
                  <div className="driver-card-content">
                    {driver.headshot_url ? (
                      <div className="driver-image">
                        <img 
                          src={driver.headshot_url} 
                          alt={driver.full_name}
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.parentElement.classList.add('reserve-placeholder');
                            e.target.parentElement.innerHTML = 'RESERVE DRIVER';
                          }}
                        />
                      </div>
                    ) : (
                      <div className="driver-image reserve-placeholder">
                        RESERVE DRIVER
                      </div>
                    )}
                    
                    <div className="driver-info">
                      <div className="driver-header-info">
                        <div className="name-number-container">
                          <h3>{formatDriverName(driver.full_name)}</h3>
                          <span className="driver-number">
                            #{driver.driver_number}
                          </span>
                        </div>
                        <div className="driver-meta-row">
                          <div className="country-flag">
                            {driver.country_code}
                            {driver.country_code && (
                              <img 
                                src={getCountryFlagUrl(driver.country_code)}
                                alt={driver.country_code}
                              />
                            )}
                          </div>
                          <span className={`standing-position 
                            ${driver.standing_position === 1 ? 'champion' : ''}
                            ${driver.standing_position > 1 && driver.standing_position <= 3 ? 'podium' : ''}
                            ${driver.standing_position > 3 && driver.standing_position < 10 ? 'top-ten' : ''}
                            ${driver.standing_position >= 10 ? 'below-ten' : ''}`}>
                            <span>Driver Position:</span>
                            <span className="position-number">{driver.standing_position}</span>
                          </span>
                        </div>
                        <div className="driver-stats-primary">
                          <div className="session-count">
                            {driver.race_count} races
                          </div>
                          <div className="points">
                            {driver.points || 0} points
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="driver-stats">
                    <div className={`wins ${!driver.wins ? 'zero-value' : ''}`}>
                      <span>🏆</span> {driver.wins || 0} wins
                    </div>
                    <div className={`podiums ${!driver.podiums ? 'zero-value' : ''}`}>
                      <span>🥇</span> {driver.podiums || 0} podiums
                    </div>
                    <div className={`fastest-laps ${!driver.fastest_laps ? 'zero-value' : ''}`}>
                      <span>⚡</span> {driver.fastest_laps || 0} fastest laps
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

export default DriversTab;