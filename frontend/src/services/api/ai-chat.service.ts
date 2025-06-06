import { API_CONFIG } from '../../constants/config';
import { F1DataService } from './f1-data.service';
import { BaseApiService } from './base-api.service';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export class AIChatService {
  public static async sendMessage(message: string, selectedYear: number): Promise<string> {
    try {
      // Get relevant data based on the message content
      const data = await this.gatherRelevantData(message, selectedYear);

      // Call backend API
      const result = await BaseApiService.request(`${API_CONFIG.ENDPOINTS.AI}/chat`, {
        method: 'POST',
        body: JSON.stringify({
          message,
          data
        })
      });

      return result.response;
    } catch (error) {
      console.error('Error in AI chat:', error);
      return 'Sorry, I encountered an error while processing your request.';
    }
  }

  private static async gatherRelevantData(message: string, selectedYear: number): Promise<any> {
    const data: any = {};
    
    // Check if message mentions drivers
    if (message.toLowerCase().includes('driver')) {
      data.drivers = await F1DataService.getDrivers(selectedYear);
    }
    
    // Check if message mentions constructors
    if (message.toLowerCase().includes('constructor') || message.toLowerCase().includes('team')) {
      data.constructors = await F1DataService.getConstructors(selectedYear);
    }
    
    // Check if message mentions sessions
    if (message.toLowerCase().includes('session') || message.toLowerCase().includes('race')) {
      data.sessions = await F1DataService.getSessions(selectedYear);
    }
    
    // Always include overview data
    data.overview = await F1DataService.getOverview(selectedYear);
    
    return data;
  }
} 