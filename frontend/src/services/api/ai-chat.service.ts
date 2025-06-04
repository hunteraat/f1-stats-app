import { F1DataService } from './f1-data.service';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export class AIChatService {
  private static instance: AIChatService;
  private messageHistory: ChatMessage[] = [];
  private readonly API_URL = 'http://localhost:5000/api/ai/chat';

  private constructor() {}

  public static getInstance(): AIChatService {
    if (!AIChatService.instance) {
      AIChatService.instance = new AIChatService();
    }
    return AIChatService.instance;
  }

  public async sendMessage(message: string, selectedYear: number): Promise<string> {
    // Add user message to history
    this.messageHistory.push({ role: 'user', content: message });

    try {
      // Get relevant data based on the message content
      const data = await this.gatherRelevantData(message, selectedYear);
      
      // Call backend API
      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          data
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const result = await response.json();
      
      // Add assistant response to history
      this.messageHistory.push({ role: 'assistant', content: result.response });
      
      return result.response;
    } catch (error) {
      console.error('Error in AI chat:', error);
      return 'Sorry, I encountered an error while processing your request.';
    }
  }

  private async gatherRelevantData(message: string, selectedYear: number): Promise<any> {
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

  public clearHistory(): void {
    this.messageHistory = [];
  }
} 