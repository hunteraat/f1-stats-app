import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchF1Data, syncF1Data, getSyncStatus, SyncStatus } from '../services/api/f1';
import { useInterval } from './useInterval';

export const useF1Data = (year: number) => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const isInitializedRef = useRef(false);
  const isSyncingRef = useRef(false);

  const checkSyncStatus = useCallback(async () => {
    try {
      const status = await getSyncStatus(year);
      setSyncStatus(status);
      return status;
    } catch (err) {
      console.error('Failed to check sync status:', err);
      return null;
    }
  }, [year]);

  // Poll for sync status every 2 seconds when syncing
  useInterval(
    checkSyncStatus,
    syncStatus?.status === 'in_progress' ? 2000 : null
  );

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await fetchF1Data(year);
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch F1 data');
    } finally {
      setIsLoading(false);
    }
  }, [year]);

  const syncData = useCallback(async () => {
    if (isSyncingRef.current) return;
    
    try {
      isSyncingRef.current = true;
      setError(null);
      await syncF1Data(year);
      await checkSyncStatus();
    } catch (err: any) {
      setError(err.message || 'Failed to sync F1 data');
    } finally {
      isSyncingRef.current = false;
    }
  }, [year, checkSyncStatus]);

  // Initial data load and sync check
  useEffect(() => {
    if (isInitializedRef.current) return;
    isInitializedRef.current = true;

    const initialize = async () => {
      // Check sync status first
      const status = await checkSyncStatus();
      
      // If it's the current year, check if we need an incremental update
      const isCurrentYear = year === new Date().getFullYear();
      if (isCurrentYear && status?.last_incremental) {
        const lastSync = new Date(status.last_incremental);
        const now = new Date();
        const hoursSinceLastSync = (now.getTime() - lastSync.getTime()) / (1000 * 60 * 60);
        
        // If more than 1 hour since last sync, trigger an incremental update
        if (hoursSinceLastSync > 1) {
          await syncData();
        }
      }
      
      // Fetch initial data
      await fetchData();
    };

    initialize();
  }, [year, checkSyncStatus, fetchData, syncData]);

  // Refetch data when sync completes
  useEffect(() => {
    if (syncStatus?.status === 'completed') {
      fetchData();
    }
  }, [syncStatus?.status, fetchData]);

  return {
    data,
    isLoading,
    error,
    syncData,
    syncStatus
  };
}; 