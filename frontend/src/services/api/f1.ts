import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export interface SyncResponse {
  success: boolean;
  message: string;
  drivers_processed?: number;
  sessions_processed?: number;
  year?: number;
  cached?: boolean;
  error?: string;
}

export interface SyncStatus {
  status: 'not_started' | 'in_progress' | 'completed' | 'error';
  progress: number;
  message: string;
  last_synced: string | null;
  last_incremental: string | null;
}

export const fetchF1Data = async (year: number) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/data/${year}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.error || 'Failed to fetch F1 data');
  }
};

export const syncF1Data = async (year: number): Promise<SyncResponse> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/sync/data/${year}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.error || 'Failed to sync F1 data');
  }
};

export const getSyncStatus = async (year: number): Promise<SyncStatus> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/sync/status/${year}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.error || 'Failed to get sync status');
  }
}; 