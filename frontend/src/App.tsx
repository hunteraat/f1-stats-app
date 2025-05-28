import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, CircularProgress } from '@mui/material';
import { useF1Data } from './hooks/useF1Data';
import TabNavigation from './components/TabNavigation/TabNavigation.jsx';
import OverviewTab from './components/OverviewTab/OverviewTab.jsx';
import DriversTab from './components/DriversTab/DriversTab.jsx';
import SessionsTab from './components/SessionsTab/SessionsTab.jsx';
import YearSelector from './components/YearSelector/YearSelector.jsx';
import ErrorMessage from './components/ErrorMessage/ErrorMessage.jsx';
import SyncStatus from './components/SyncStatus/SyncStatus.jsx';

const App: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [activeTab, setActiveTab] = useState('overview');
  const { data, isLoading, error, syncStatus } = useF1Data(selectedYear);

  // Generate available years (from 2018 to current year)
  const availableYears = Array.from(
    { length: new Date().getFullYear() - 2017 },
    (_, i) => ({
      year: new Date().getFullYear() - i,
      synced: true,
      drivers_count: 20
    })
  );

  const renderContent = () => {
    if (!data) return null;

    switch (activeTab) {
      case 'overview':
        return <OverviewTab stats={data} selectedYear={selectedYear} />;
      case 'drivers':
        return (
          <DriversTab
            drivers={data.drivers}
            selectedYear={selectedYear}
            onFetchSessionPositions={() => {}}
          />
        );
      case 'sessions':
        return <SessionsTab sessions={data.sessions} selectedYear={selectedYear} />;
      default:
        return null;
    }
  };

  return (
    <div className="app-container">
      <TabNavigation
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      
      <main className="main-content">
        <Container maxWidth="lg">
          <Box sx={{ pt: 1, pb: 2 }}>
            {error && <ErrorMessage error={error} onDismiss={() => {}} />}

            <SyncStatus syncStatus={syncStatus} />

            <YearSelector
              availableYears={availableYears}
              selectedYear={selectedYear}
              onYearChange={setSelectedYear}
              loading={isLoading}
            />

            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <CircularProgress />
              </Box>
            ) : (
              renderContent()
            )}
          </Box>
        </Container>
      </main>
    </div>
  );
};

export default App; 