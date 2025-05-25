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
  const [loading, setLoading] = useState(true);
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

  // Fetch data for selected year
  const fetchData = async (year = selectedYear) => {
    try {
      setLoading(true);
      
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
      setLoading(false);
    }
  };

  // Handle year selection
  const handleYearChange = async (year) => {
    setSelectedYear(year);
    setSelectedDriver(null);
    setDriverSessions([]);
    
    // Check if year is already synced
    const yearInfo = availableYears.find(y => y.year === year);
    
    if (!yearInfo || !yearInfo.synced) {
      // Need to sync data first
      await syncF1Data(year);
    } else {
      // Just fetch existing data
      await fetchData(year);
    }
  };

  // Sync F1 data from OpenF1 API
  const syncF1Data = async (year = selectedYear) => {
    try {
      setSyncLoading(true);
      const result = await ApiService.syncData(year);

      if (result.cached) {
        // Data was already cached, just refresh
        await fetchData(year);
        return;
      }

      // Refresh data after sync
      await Promise.all([
        fetchData(year),
        fetchAvailableYears()
      ]);
      
      if (!result.cached) {
        alert(`✅ ${result.message}\n📊 Processed ${result.drivers_processed} drivers and ${result.sessions_processed} sessions`);
      }
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
      await fetchAvailableYears();
      await handleYearChange(selectedYear);
    };
    
    initializeApp();
  }, []);

  return (
    <div className="App">
      <Header 
        onSync={() => syncF1Data(selectedYear)} 
        syncLoading={syncLoading}
      />

      <div className="controls-section">
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
      </div>

      <main className="main-content">
        {error && (
          <ErrorMessage 
            error={error} 
            onDismiss={() => setError(null)} 
          />
        )}

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
      </main>
    </div>
  );
}

export default App;