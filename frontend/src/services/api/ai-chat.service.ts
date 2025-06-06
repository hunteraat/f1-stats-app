import { API_CONFIG } from '../../constants/config';
import { BaseApiService } from './base-api.service';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export class AIChatService {
  public static async sendMessage(
    messages: ChatMessage[],
    selectedYear: number
  ): Promise<string> {
    try {
      // Call backend API with the entire message history and year
      const result = await BaseApiService.request(
        `${API_CONFIG.ENDPOINTS.AI}/chat`,
        {
          method: 'POST',
          body: JSON.stringify({
            messages,
            year: selectedYear,
          }),
        }
      );

      return result.response;
    } catch (error) {
      return 'Sorry, I encountered an error while processing your request.';
    }
  }
}
