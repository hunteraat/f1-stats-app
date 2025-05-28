import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchF1Data, syncF1Data, getSyncStatus, SyncStatus } from '../services/api/f1-sync.service';
import { useInterval } from './useInterval';

export interface F1Data {
  drivers: Array<{
    driverId: string;
    code: string;
    url: string;
    givenName: string;
    familyName: string;
    full_name: string;
    dateOfBirth: string;
    nationality: string;
    team_name: string;
    team_colour: string;
    driver_number: number;
    country_code: string;
    session_count: number;
    race_count: number;
    wins: number;
    podiums: number;
    fastest_laps: number;
    points: number;
    standing_position: number;
    team_points: number;
    constructor_position: number | null;
  }>;
  sessions: Array<{
    id: number;
    sessionId: string;
    session_key: string;
    session_name: string;
    year: number;
    round: number;
    circuitId: string;
    circuitName: string;
    circuit_short_name: string;
    location: string;
    country_name: string;
    date: string;
    date_start: string | null;
    time: string;
    sessionType: string;
    session_type: string;
    driver_count: number;
    lap_count: number;
  }>;
  stats: {
    total_drivers: number;
    active_drivers: number;
    total_sessions: number;
    latest_session: {
      name: string;
      location: string;
      date: string | null;
    } | null;
  };
}

export const useF1Data = (year: number) => {
  const [data, setData] = useState<F1Data | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const lastSyncTime = useRef<number>(0);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await fetchF1Data(year);
      setData(result);
      lastSyncTime.current = Date.now();
    } catch (err: any) {
      setError(err.message || 'Failed to fetch F1 data');
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, [year]);

  const checkSyncStatus = useCallback(async () => {
    try {
      const status = await getSyncStatus(year);
      setSyncStatus(status);
      return status;
    } catch (err: any) {
      console.error('Failed to check sync status:', err);
      return null;
    }
  }, [year]);

  const handleSync = async () => {
    try {
      setIsSyncing(true);
      setError(null);
      const result = await syncF1Data(year);
      if (result.success) {
        await fetchData();
      } else {
        setError(result.error || 'Sync failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to sync F1 data');
    } finally {
      setIsSyncing(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Check sync status periodically only when syncing
  useInterval(async () => {
    if (!isSyncing) return;

    const status = await checkSyncStatus();
    if (status?.status === 'completed') {
      setIsSyncing(false);
      await fetchData();
    } else if (status?.status === 'error') {
      setIsSyncing(false);
      setError('Sync failed');
    }
  }, isSyncing ? 5000 : null);

  return {
    data,
    isLoading,
    error,
    syncStatus,
    isSyncing,
    handleSync,
    refetch: fetchData
  };
}; 