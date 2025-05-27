import { useState, useCallback, useEffect, useRef } from 'react';
import { F1ApiService } from '../services/api/f1.service';
import { APP_CONFIG } from '../constants/config';

export const useF1Data = () => {
  const [selectedYear, setSelectedYear] = useState(APP_CONFIG.DEFAULT_YEAR);
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
  const initialized = useRef(false);

  const fetchAvailableYears = useCallback(async () => {
    try {
      const years = await F1ApiService.getAvailableYears();
      setAvailableYears(years);
      return years;
    } catch (err) {
      setError(`Failed to fetch available years: ${err.message}`);
      return [];
    }
  }, []);

  const fetchData = useCallback(async (year = selectedYear) => {
    try {
      setDataLoading(true);
      
      const [driversData, sessionsData, statsData] = await Promise.all([
        F1ApiService.getDrivers(year),
        F1ApiService.getSessions(year),
        F1ApiService.getStatsummary(year)
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
  }, [selectedYear]);

  const syncF1Data = useCallback(async (year = selectedYear) => {
    try {
      setSyncLoading(true);
      setError(null);
      
      setDrivers([]);
      setSessions([]);
      setStats(null);
      
      const result = await F1ApiService.syncData(year);

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
  }, [selectedYear, fetchData, fetchAvailableYears]);

  const handleYearChange = useCallback(async (year) => {
    if (syncLoading) return;
    
    setSelectedYear(year);
    setSelectedDriver(null);
    setDriverSessions([]);
    
    const yearInfo = availableYears.find(y => y.year === year);
    
    if (!yearInfo || !yearInfo.synced) {
      setDrivers([]);
      setSessions([]);
      setStats(null);
      await syncF1Data(year);
    } else {
      await fetchData(year);
    }
  }, [syncLoading, availableYears, syncF1Data, fetchData]);

  const fetchDriverSessions = useCallback(async (driverId) => {
    try {
      const data = await F1ApiService.getDriverSessions(driverId, selectedYear);
      setDriverSessions(data.sessions);
      setSelectedDriver(data.driver);
    } catch (err) {
      setError(`Failed to fetch driver sessions: ${err.message}`);
    }
  }, [selectedYear]);

  const fetchSessionPositions = useCallback(async (sessionId) => {
    try {
      return await F1ApiService.getSessionPositions(sessionId);
    } catch (err) {
      setError(`Failed to fetch session positions: ${err.message}`);
      return null;
    }
  }, []);

  // Initialize app data
  useEffect(() => {
    const initializeApp = async () => {
      if (initialized.current) return;
      initialized.current = true;

      try {
        const years = await fetchAvailableYears();
        const yearInfo = years.find(y => y.year === selectedYear);
        
        if (!yearInfo || !yearInfo.synced) {
          await syncF1Data(selectedYear);
        } else {
          await fetchData(selectedYear);
        }
      } catch (err) {
        setError(`Failed to initialize app: ${err.message}`);
      } finally {
        setInitialLoading(false);
      }
    };
    
    initializeApp();
  }, []); // Empty dependency array since we use initialized.current to prevent re-runs

  return {
    // State
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
    
    // Actions
    setInitialLoading,
    setError,
    fetchAvailableYears,
    fetchData,
    syncF1Data,
    handleYearChange,
    fetchDriverSessions,
    fetchSessionPositions,
    setSelectedDriver
  };
}; 