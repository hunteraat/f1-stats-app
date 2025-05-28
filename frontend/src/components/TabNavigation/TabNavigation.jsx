import React from 'react';
import './TabNavigation.css';

const TabNavigation = ({ activeTab, onTabChange }) => {
  return (
    <div className="tab-navigation">
      <button 
        className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
        onClick={() => onTabChange('overview')}
      >
        📊 Overview
      </button>
      <button 
        className={`tab-button ${activeTab === 'drivers' ? 'active' : ''}`}
        onClick={() => onTabChange('drivers')}
      >
        🏎️ Drivers
      </button>
      <button 
        className={`tab-button ${activeTab === 'sessions' ? 'active' : ''}`}
        onClick={() => onTabChange('sessions')}
      >
        🏁 Sessions
      </button>
    </div>
  );
};

export default TabNavigation; 