import React, { useState } from 'react';
import TabNavigation from './components/TabNavigation';
import OverviewTab from './components/OverviewTab';
import DriversTab from './components/DriversTab';
import SessionsTab from './components/SessionsTab';
import YearSelector from './components/YearSelector';
import ErrorMessage from './components/ErrorMessage';
import { useF1Data } from './hooks/useF1Data';
import { APP_CONFIG } from './constants/config';
import './styles/components/YearSelector.css';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const {
    selectedYear,
    availableYears,
    drivers,
    sessions,
    stats,
    initialLoading,
    dataLoading,
    syncLoading,
    error,
    selectedDriver,
    driverSessions,
    setError,
    handleYearChange,
    fetchDriverSessions,
    fetchSessionPositions,
    setSelectedDriver
  } = useF1Data();

  if (initialLoading) {
    return (
      <div className="App">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          fontSize: '18px' 
        }}>
          {APP_CONFIG.LOADING_MESSAGE}
        </div>
      </div>
    );
  }

  const currentYearInfo = availableYears.find(y => y.year === selectedYear);
  const hasDataForYear = currentYearInfo && currentYearInfo.synced;

  return (
    <div className="App">
      <YearSelector
        availableYears={availableYears}
        selectedYear={selectedYear}
        onYearChange={handleYearChange}
        loading={syncLoading}
      />
      
      <TabNavigation 
        activeTab={activeTab} 
        onTabChange={setActiveTab} 
      />

      {(syncLoading || dataLoading) && (
        <div className="loading-indicator">
          {syncLoading ? 
            `🔄 Downloading F1 data for ${selectedYear}... This may take a moment.` : 
            '📊 Loading data...'
          }
        </div>
      )}

      <main className="main-content">
        {error && (
          <ErrorMessage 
            error={error} 
            onDismiss={() => setError(null)} 
          />
        )}

        {hasDataForYear && (
          <>
            {activeTab === 'overview' && (
              <OverviewTab 
                stats={stats} 
                selectedYear={selectedYear}
              />
            )}

            {activeTab === 'drivers' && (
              <DriversTab 
                drivers={drivers} 
                selectedDriver={selectedDriver}
                driverSessions={driverSessions}
                selectedYear={selectedYear}
                onDriverSelect={fetchDriverSessions}
                onBackToDrivers={() => setSelectedDriver(null)}
                onFetchSessionPositions={fetchSessionPositions}
              />
            )}

            {activeTab === 'sessions' && (
              <SessionsTab 
                sessions={sessions} 
                selectedYear={selectedYear}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;