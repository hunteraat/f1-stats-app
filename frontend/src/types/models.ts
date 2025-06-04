export interface Driver {
  id: number;
  driver_number: number;
  full_name: string;
  team_name: string;
  team_colour: string;
  country_code: string;
  headshot_url: string;
  last_updated: string | null;
  session_count: number;
  races: number;
  wins: number;
  podiums: number;
  fastest_laps: number;
  points: number;
  standing_position: number;
  team_points: number;
  constructor_position: number | null;
  year: number;
  position: number;
  average_position: number;
  is_active: boolean;
}

export interface Session {
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
  driver_number: number;
  full_name: string;
  team_name: string;
  final_position: number | null;
  fastest_lap: boolean;
  points: number;
}

export interface DriverSession {
  driver_number: number;
  full_name: string;
  team_name: string;
  session_name: string;
  session_type: string;
  location: string;
  date_start: string;
  final_position: number | null;
  fastest_lap: boolean;
  points: number;
  year: number;
}

export interface Constructor {
    team_name: string;
    team_colour: string;
    position: number;
    points: number;
    wins: number;
    podiums: number;
    fastest_laps: number;
    year: number;
    races: number;
}

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

export interface Overview {
  total_drivers: number;
  active_drivers: number;
  total_sessions: number;
  latest_session: {
    name: string;
    location: string;
    date: string | null;
  } | null;
}

export interface SyncResult {
  cached: boolean;
  drivers_processed: number;
  sessions_processed: number;
  status: 'not_started' | 'in_progress' | 'completed' | 'error';
} 