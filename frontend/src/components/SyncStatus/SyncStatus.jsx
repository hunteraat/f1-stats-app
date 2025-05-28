import React from 'react';
import './SyncStatus.css';

const SyncStatus = ({ syncStatus }) => {
  if (!syncStatus || syncStatus.status !== 'in_progress') {
    return null;
  }

  return (
    <div className="sync-status">
      <div className="sync-progress">
        <div 
          className="progress-bar"
          style={{ width: `${syncStatus.progress}%` }}
        />
      </div>
      <div className="sync-info">
        <span className="sync-message">{syncStatus.message}</span>
        <span className="sync-percentage">{Math.round(syncStatus.progress)}%</span>
      </div>
    </div>
  );
};

export default SyncStatus; 