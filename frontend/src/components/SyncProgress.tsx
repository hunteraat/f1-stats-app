import React from 'react';
import { SyncStatus } from '../services/api/f1';
import { LinearProgress, Box, Typography, Paper } from '@mui/material';

interface SyncProgressProps {
  syncStatus: SyncStatus | null;
}

export const SyncProgress: React.FC<SyncProgressProps> = ({ syncStatus }) => {
  if (!syncStatus || syncStatus.status === 'not_started') {
    return null;
  }

  const getStatusColor = () => {
    switch (syncStatus.status) {
      case 'completed':
        return 'success.main';
      case 'error':
        return 'error.main';
      case 'in_progress':
        return 'primary.main';
      default:
        return 'text.primary';
    }
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 2, 
        mb: 2,
        backgroundColor: syncStatus.status === 'error' ? 'error.light' : 'background.paper'
      }}
    >
      <Box sx={{ width: '100%', mb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body1" color={getStatusColor()}>
            {syncStatus.message || 'Syncing data...'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {syncStatus.progress.toFixed(0)}%
          </Typography>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={syncStatus.progress} 
          color={syncStatus.status === 'error' ? 'error' : 'primary'}
        />
      </Box>
      {syncStatus.last_synced && (
        <Typography variant="caption" color="text.secondary">
          Last synced: {new Date(syncStatus.last_synced).toLocaleString()}
          {syncStatus.last_incremental && ' (Incremental)'}
        </Typography>
      )}
    </Paper>
  );
}; 