import axios from 'axios';
import { F1Data } from '../../hooks/useF1Data';

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

type DriverResponse = Array<{
  id: number;
  driver_number: number;
  full_name: string;
  team_name: string;
  team_colour: string;
  country_code: string;
  headshot_url: string;
  last_updated: string | null;
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

type SessionResponse = Array<{
  id: number;
  session_key: string;
  session_name: string;
  date_start: string | null;
  location: string;
  country_name: string;
  circuit_short_name: string;
  year: number;
  session_type: string;
  driver_count: number;
  lap_count?: number;
}>;

export const fetchF1Data = async (year: number): Promise<F1Data> => {
  try {
    // Fetch drivers and sessions in parallel
    const [driversResponse, sessionsResponse] = await Promise.all([
      axios.get<DriverResponse>(`${API_BASE_URL}/drivers`, { params: { year } }),
      axios.get<SessionResponse>(`${API_BASE_URL}/sessions`, { params: { year } })
    ]);

    // Calculate overview stats
    const stats = {
      total_drivers: driversResponse.data.length,
      active_drivers: driversResponse.data.filter(d => d.session_count > 0).length,
      total_sessions: sessionsResponse.data.length,
      latest_session: sessionsResponse.data.length > 0 ? {
        name: sessionsResponse.data[0].session_name,
        location: sessionsResponse.data[0].location,
        date: sessionsResponse.data[0].date_start
      } : null
    };

    // Transform the data to match the F1Data interface
    return {
      drivers: driversResponse.data.map(driver => ({
        driverId: driver.id.toString(),
        code: driver.country_code,
        url: driver.headshot_url,
        givenName: driver.full_name.split(' ')[0],
        familyName: driver.full_name.split(' ').slice(1).join(' '),
        full_name: driver.full_name,
        dateOfBirth: '', // Not available in the API response
        nationality: driver.country_code,
        team_name: driver.team_name,
        team_colour: driver.team_colour,
        driver_number: driver.driver_number,
        country_code: driver.country_code,
        session_count: driver.session_count,
        race_count: driver.race_count,
        wins: driver.wins,
        podiums: driver.podiums,
        fastest_laps: driver.fastest_laps,
        points: driver.points,
        standing_position: driver.standing_position,
        team_points: driver.team_points,
        constructor_position: driver.constructor_position
      })),
      sessions: sessionsResponse.data.map(session => ({
        id: session.id,
        sessionId: session.id.toString(),
        session_key: session.session_key,
        session_name: session.session_name,
        year: session.year,
        round: 0, // Not available in the API response
        circuitId: session.circuit_short_name,
        circuitName: session.location,
        circuit_short_name: session.circuit_short_name,
        location: session.location,
        country_name: session.country_name,
        date: session.date_start || '',
        date_start: session.date_start,
        time: '', // Not available in the API response
        sessionType: session.session_type,
        session_type: session.session_type,
        driver_count: session.driver_count,
        lap_count: session.lap_count || 0
      })),
      stats
    };
  } catch (error: any) {
    throw new Error(error.response?.data?.error || 'Failed to fetch F1 data');
  }
};

export const syncF1Data = async (year: number): Promise<SyncResponse> => {
  try {
    const response = await axios.post<SyncResponse>(`${API_BASE_URL}/sync/data/${year}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.error || 'Failed to sync F1 data');
  }
};

export const getSyncStatus = async (year: number): Promise<SyncStatus> => {
  try {
    const response = await axios.get<SyncStatus>(`${API_BASE_URL}/sync/status/${year}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.error || 'Failed to get sync status');
  }
}; 