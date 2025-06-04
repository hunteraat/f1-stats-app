import React from 'react';
import './TabNavigation.css';
import { TabTypes } from '../../constants/common-constants';

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="tab-navigation">
      <button 
        className={`tab-button ${activeTab === TabTypes.OVERVIEW ? 'active' : ''}`}
        onClick={() => onTabChange(TabTypes.OVERVIEW)}
      >
        Overview
      </button>
      <button 
        className={`tab-button ${activeTab === TabTypes.DRIVERS ? 'active' : ''}`}
        onClick={() => onTabChange(TabTypes.DRIVERS)}
      >
        Drivers
      </button>
      <button 
        className={`tab-button ${activeTab === TabTypes.CONSTRUCTORS ? 'active' : ''}`}
        onClick={() => onTabChange(TabTypes.CONSTRUCTORS)}
      >
        Constructors
      </button>
      <button 
        className={`tab-button ${activeTab === TabTypes.SESSIONS ? 'active' : ''}`}
        onClick={() => onTabChange(TabTypes.SESSIONS)}
      >
        Sessions
      </button>
    </div>
  );
};

export default TabNavigation; 