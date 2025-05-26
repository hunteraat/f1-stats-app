import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import TabNavigation from './components/TabNavigation';
import OverviewTab from './components/OverviewTab';
import DriversTab from './components/DriversTab';
import SessionsTab from './components/SessionsTab';
import YearSelector from './components/YearSelector';
import ErrorMessage from './components/ErrorMessage';
import { ApiService } from './services/ApiService';
import './App.css';

function App() {
  const [selectedYear, setSelectedYear] = useState(2025);
  const [availableYears, setAvailableYears] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [driverSessions, setDriverSessions] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch available years
  const fetchAvailableYears = async () => {
    try {
      const years = await ApiService.getAvailableYears();
      setAvailableYears(years);
    } catch (err) {
      setError(`Failed to fetch available years: ${err.message}`);
    }
  };

  // Fetch data for selected year (only if synced)
  const fetchData = async (year = selectedYear) => {
    try {
      setDataLoading(true);
      
      const [driversData, sessionsData, statsData] = await Promise.all([
        ApiService.getDrivers(year),
        ApiService.getSessions(year),
        ApiService.getStatsummary(year)
      ]);

      setDrivers(driversData);
      setSessions(sessionsData);
      setStats(statsData);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch data: ${err.message}`);
    } finally {
      setDataLoading(false);
    }
  };

  // Handle year selection
  const handleYearChange = async (year) => {
    if (syncLoading) return; // Prevent year changes during sync
    
    setSelectedYear(year);
    setSelectedDriver(null);
    setDriverSessions([]);
    
    // Check if year is already synced
    const yearInfo = availableYears.find(y => y.year === year);
    
    if (!yearInfo || !yearInfo.synced) {
      // Clear existing data and automatically start sync
      setDrivers([]);
      setSessions([]);
      setStats(null);
      await syncF1Data(year);
    } else {
      // Fetch existing data
      await fetchData(year);
    }
  };

  // Sync F1 data from OpenF1 API - now consolidates all API calls by year
  const syncF1Data = async (year = selectedYear) => {
    try {
      setSyncLoading(true);
      setError(null);
      
      // Clear existing data to show we're refreshing
      setDrivers([]);
      setSessions([]);
      setStats(null);
      
      const result = await ApiService.syncData(year);

      // Refresh data after sync
      await Promise.all([
        fetchData(year),
        fetchAvailableYears()
      ]);
      
      if (!result.cached) {
        console.log(`✅ Synced data for ${year}\n📊 Processed ${result.drivers_processed} drivers and ${result.sessions_processed} sessions`);
      }
    } catch (err) {
      setError(`Sync failed: ${err.message}`);
      console.error('Sync failed:', err);
    } finally {
      setSyncLoading(false);
    }
  };

  // Fetch driver sessions
  const fetchDriverSessions = async (driverId) => {
    try {
      const data = await ApiService.getDriverSessions(driverId, selectedYear);
      setDriverSessions(data.sessions);
      setSelectedDriver(data.driver);
    } catch (err) {
      setError(`Failed to fetch driver sessions: ${err.message}`);
    }
  };

  // Fetch session positions
  const fetchSessionPositions = async (sessionId) => {
    try {
      return await ApiService.getSessionPositions(sessionId);
    } catch (err) {
      setError(`Failed to fetch session positions: ${err.message}`);
      return null;
    }
  };

  useEffect(() => {
    const initializeApp = async () => {
      try {
        // First load available years (this is fast)
        await fetchAvailableYears();
        
        // Then check if selected year has data
        const yearInfo = availableYears.find(y => y.year === selectedYear);
        if (yearInfo && yearInfo.synced) {
          await fetchData(selectedYear);
        }
      } catch (err) {
        setError(`Failed to initialize app: ${err.message}`);
      } finally {
        setInitialLoading(false);
      }
    };
    
    initializeApp();
  }, []);

  // Show initial loading only for the first app load
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
          Loading F1 Statistics App...
        </div>
      </div>
    );
  }

  // Check if current year has data
  const currentYearInfo = availableYears.find(y => y.year === selectedYear);
  const hasDataForYear = currentYearInfo && currentYearInfo.synced;

  return (
    <div className="App">
      <Header />

      <div className="controls-section">
        <YearSelector
          availableYears={availableYears}
          selectedYear={selectedYear}
          onYearChange={handleYearChange}
          loading={syncLoading} // Disable during sync
        />
        
        <TabNavigation 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
        />
      </div>

      {/* Loading indicator for data operations */}
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