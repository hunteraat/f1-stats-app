import { BaseApiService } from './base-api.service';
import { API_CONFIG } from '../../constants/config';
import { Driver, Session, Overview, SyncResult, SyncStatus, Constructor, DriverSession } from '../../types/models';

export class F1DataService extends BaseApiService {
  static async getAvailableYears(): Promise<{ year: number; synced: boolean }[]> {
    return this.request(API_CONFIG.ENDPOINTS.YEARS);
  }

  static async getDrivers(year?: number): Promise<Driver[]> {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.DRIVERS}${params}`);
  }

  static async getDriverSessions(driverNumber: number, year?: number): Promise<DriverSession[]> {
    let params = `?driver_number=${driverNumber}`;
    if (year) {
      params += `&year=${year}`;
    }
    return this.request(`${API_CONFIG.ENDPOINTS.DRIVERS}/sessions${params}`);
  }

  static async getSessions(year?: number): Promise<Session[]> {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.SESSIONS}${params}`);
  }

  static async getSessionPositions(sessionId: string): Promise<any> {
    return this.request(`${API_CONFIG.ENDPOINTS.SESSIONS}/${sessionId}/positions`);
  }

  static async getOverview(year?: number): Promise<Overview> {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.OVERVIEW}${params}`);
  }

  static async getConstructors(year?: number): Promise<Constructor[]> {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.CONSTRUCTORS}${params}`);
  }

  static async syncData(year: number): Promise<SyncResult> {
    return this.request(`${API_CONFIG.ENDPOINTS.SYNC}/data/${year}`, {
      method: 'POST',
    });
  }

  static async getSyncStatus(year: number): Promise<SyncStatus> {
    return this.request(`${API_CONFIG.ENDPOINTS.SYNC}/status/${year}`);
  }
} 