import { BaseApiService } from './base-api.service';
import { API_CONFIG } from '../../constants/config';

export class F1ApiService extends BaseApiService {
  static async getAvailableYears() {
    return this.request(API_CONFIG.ENDPOINTS.YEARS);
  }

  static async getDrivers(year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.DRIVERS}${params}`);
  }

  static async getDriverSessions(driverId, year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.DRIVERS}/${driverId}/sessions${params}`);
  }

  static async getSessions(year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.SESSIONS}${params}`);
  }

  static async getSessionPositions(sessionId) {
    return this.request(`${API_CONFIG.ENDPOINTS.SESSIONS}/${sessionId}/positions`);
  }

  static async getStatsummary(year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`${API_CONFIG.ENDPOINTS.STATS}${params}`);
  }

  static async syncData(year) {
    return this.request(`${API_CONFIG.ENDPOINTS.SYNC}/${year}`, {
      method: 'POST',
    });
  }

  static async resetDatabase() {
    return this.request(`${API_CONFIG.ENDPOINTS.DATABASE}/reset`, {
      method: 'POST',
    });
  }
} 