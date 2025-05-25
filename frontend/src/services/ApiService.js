const API_BASE_URL = 'http://localhost:5000/api';

export class ApiService {
  static async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  static async getAvailableYears() {
    return this.request('/years');
  }

  static async getDrivers(year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`/drivers${params}`);
  }

  static async getDriverSessions(driverId, year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`/drivers/${driverId}/sessions${params}`);
  }

  static async getSessions(year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`/sessions${params}`);
  }

  static async getSessionPositions(sessionId) {
    return this.request(`/sessions/${sessionId}/positions`);
  }

  static async getStatsummary(year = null) {
    const params = year ? `?year=${year}` : '';
    return this.request(`/stats/summary${params}`);
  }

  static async syncData(year) {
    return this.request(`/sync-data/${year}`, {
      method: 'POST',
    });
  }

  static async resetDatabase() {
    return this.request('/database/reset', {
      method: 'POST',
    });
  }
}