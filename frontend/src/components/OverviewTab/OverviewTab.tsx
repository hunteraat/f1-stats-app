import React, { useState, useEffect } from 'react';
import { Box, CircularProgress, TextField, Paper } from '@mui/material';

import { F1DataService } from '../../services/api/f1-data.service';
import { AIChatService, ChatMessage } from '../../services/api/ai-chat.service';
import './OverviewTab.css';
import { Overview } from '../../types/models';
import { TabTypes } from '../../constants/common-constants';

interface OverviewTabProps {
  selectedYear: number;
  onTabChange: (tab: string) => void;
}

const OverviewTab: React.FC<OverviewTabProps> = ({
  selectedYear,
  onTabChange,
}) => {
  const [stats, setStats] = useState<Overview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aiQuestion, setAiQuestion] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await F1DataService.getOverview(selectedYear);
        setStats(response);
      } catch (error) {
        setError('Failed to fetch statistics');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [selectedYear]);

  const handleSendMessage = async () => {
    if (!aiQuestion.trim()) {
      return;
    }

    const userMessage: ChatMessage = { role: 'user', content: aiQuestion };
    const newMessages: ChatMessage[] = [...chatMessages, userMessage];

    setChatMessages(newMessages);
    setAiQuestion('');
    setIsProcessing(true);
    
    // Add loading message
    setChatMessages(prev => [...prev, { role: 'assistant', content: '...' }]);

    try {
      const response = await AIChatService.sendMessage(newMessages, selectedYear);
      
      // Replace loading message with actual response
      setChatMessages(prev => {
        const updatedMessages = [...prev];
        const loadingIndex = updatedMessages.findIndex(
          msg => msg.role === 'assistant' && msg.content === '...'
        );
        if (loadingIndex !== -1) {
          updatedMessages[loadingIndex] = { role: 'assistant', content: response };
        }
        return updatedMessages;
      });
    } catch (error) {
      // Replace loading message with error
      setChatMessages(prev => {
        const updatedMessages = [...prev];
        const loadingIndex = updatedMessages.findIndex(
          msg => msg.role === 'assistant' && msg.content === '...'
        );
        if (loadingIndex !== -1) {
          updatedMessages[loadingIndex] = {
            role: 'assistant',
            content: 'Sorry, I encountered an error while processing your request.',
          };
        }
        return updatedMessages;
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <div className="error-message">{error}</div>
      </Box>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="overview-container">
      <h1 className="overview-header">{selectedYear} Season Overview</h1>

      <div className="stats-grid">
        <div
          className="stat-card clickable"
          onClick={() => onTabChange(TabTypes.DRIVERS)}
        >
          <h3>Total Drivers</h3>
          <div className="stat-value">{stats.total_drivers}</div>
        </div>
        <div
          className="stat-card clickable"
          onClick={() => onTabChange(TabTypes.SESSIONS)}
        >
          <h3>Total Sessions</h3>
          <div className="stat-value">{stats.total_sessions}</div>
        </div>
        {stats.latest_session && (
          <div
            className="stat-card clickable"
            onClick={() => onTabChange(TabTypes.SESSIONS)}
          >
            <h3>Latest Session</h3>
            <div className="stat-value">{stats.latest_session.name}</div>
            <div className="stat-subtitle">
              {stats.latest_session.location}
              {stats.latest_session.date && (
                <span className="session-date">
                  {new Date(stats.latest_session.date).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="ai-question-section">
        <h2>Argue with George, the European snob:</h2>
        <div className="chat-container">
          <div className="ai-input-container">
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Raise an opinion about the current F1 season..."
              value={aiQuestion}
              onChange={e => setAiQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isProcessing}
              className="ai-input"
            />
          </div>
          <div className="chat-messages">
            {chatMessages.slice().reverse().map((message, index) => (
              <div key={index} className={`chat-message ${message.role}`}>
                <Paper 
                  elevation={1} 
                  className={`message-bubble ${message.content === '...' ? 'loading' : ''}`}
                >
                  {message.content === '...' ? (
                    <div className="loading-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  ) : (
                    message.content
                  )}
                </Paper>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewTab;
