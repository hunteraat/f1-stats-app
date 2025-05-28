import { BaseApiService } from './base-api.service';
import { API_CONFIG } from '../../constants/config';

interface Driver {
  id: string;
  name: string;
  // Add other driver properties as needed
}

interface Session {
  id: string;
  // Add other session properties as needed
}

interface StatsSummary {
  // Add stats properties as needed
}

interface SyncResult {
  cached: boolean;
  drivers_processed: number;
  sessions_processed: number;
}

export class F1DataService extends BaseApiService {
  static async getAvailableYears(): Promise<{ year: number; synced: boolean }[]> {
    return this.request(API_CONFIG.ENDPOINTS.YEARS);
  }

  static async getDrivers(year?: number): Promise<Driver[]> {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.DRIVERS}${params}`);
  }

  static async getDriverSessions(driverId: string, year?: number): Promise<{ driver: Driver; sessions: Session[] }> {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.DRIVERS}/${driverId}/sessions${params}`);
  }

  static async getSessions(year?: number): Promise<Session[]> {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.SESSIONS}${params}`);
  }

  static async getSessionPositions(sessionId: string): Promise<any> {
    return this.request(`${API_CONFIG.ENDPOINTS.SESSIONS}/${sessionId}/positions`);
  }

  static async getStatsummary(year?: number): Promise<StatsSummary> {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.STATS}${params}`);
  }

  static async syncData(year: number): Promise<SyncResult> {
    return this.request(`${API_CONFIG.ENDPOINTS.SYNC}/${year}`, {
      method: 'POST',
    });
  }

  static async resetDatabase(): Promise<void> {
    return this.request(`${API_CONFIG.ENDPOINTS.DATABASE}/reset`, {
      method: 'POST',
    });
  }
} 