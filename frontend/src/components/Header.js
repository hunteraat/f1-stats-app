import React from 'react';

const Header = ({ onSync, syncLoading }) => {
  return (
    <header className="App-header">
      <h1>🏁 F1 Driver Statistics</h1>
      <p>Formula 1 driver data powered by OpenF1 API</p>
      <div className="header-actions">
        <button 
          onClick={onSync} 
          disabled={syncLoading}
          className="sync-button"
        >
          {syncLoading ? '🔄 Syncing...' : '📥 Sync Current Year'}
        </button>
      </div>
    </header>
  );
};

export default Header;