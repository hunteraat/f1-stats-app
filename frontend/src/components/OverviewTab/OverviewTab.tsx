import React, { useState, useEffect } from 'react';
import { Box, CircularProgress, TextField, Button, Paper } from '@mui/material';
import { F1DataService } from '../../services/api/f1-data.service';
import { AIChatService, ChatMessage } from '../../services/api/ai-chat.service';
import './OverviewTab.css';
import { Overview } from '../../types/models';
import { TabTypes } from '../../constants/common-constants';

interface OverviewTabProps {
  selectedYear: number;
  onTabChange: (tab: string) => void;
}

const OverviewTab: React.FC<OverviewTabProps> = ({ selectedYear, onTabChange }) => {
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
        console.error('Error fetching stats:', error);
        setError('Failed to fetch statistics');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [selectedYear]);

  const handleSendMessage = async () => {
    if (!aiQuestion.trim()) return;

    setIsProcessing(true);
    try {
      const response = await AIChatService.sendMessage(aiQuestion, selectedYear);
      setChatMessages(prev => [
        { role: 'assistant', content: response },
        { role: 'user', content: aiQuestion },
        ...prev
      ]);
      setAiQuestion('');
    } catch (error) {
      console.error('Error sending message:', error);
      setChatMessages(prev => [
        { role: 'assistant', content: 'Sorry, I encountered an error while processing your request.' },
        { role: 'user', content: aiQuestion },
        ...prev
      ]);
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
        <div className="stat-card clickable" onClick={() => onTabChange(TabTypes.DRIVERS)}>
          <h3>Total Drivers</h3>
          <div className="stat-value">{stats.total_drivers}</div>
        </div>
        <div className="stat-card clickable" onClick={() => onTabChange(TabTypes.SESSIONS)}>
          <h3>Total Sessions</h3>
          <div className="stat-value">{stats.total_sessions}</div>
        </div>
        {stats.latest_session && (
          <div className="stat-card clickable" onClick={() => onTabChange(TabTypes.SESSIONS)}>
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
        <h2>Ask AI:</h2>
        <div className="chat-container">
          <div className="ai-input-container">
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask any question about the current F1 season..."
              value={aiQuestion}
              onChange={(e) => setAiQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isProcessing}
              className="ai-input"
            />
          </div>
          <div className="chat-messages">
            {chatMessages.map((message, index) => (
              <div key={index} className={`chat-message ${message.role}`}>
                <Paper elevation={1} className="message-bubble">
                  {message.content}
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