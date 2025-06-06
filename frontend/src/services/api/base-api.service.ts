import { API_CONFIG } from '../../constants/config';

interface RequestOptions extends RequestInit {
  headers?: HeadersInit;
}

export class BaseApiService {
  static async request(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<any> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error(`API Request failed for ${endpoint}:`, error);
      throw error;
    }
  }
}
