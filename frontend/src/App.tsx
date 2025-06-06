import React, { useState } from 'react';

import './App.css';
import TabNavigation from './components/TabNavigation/TabNavigation';
import OverviewTab from './components/OverviewTab/OverviewTab';
import DriversTab from './components/DriversTab';
import ConstructorsTab from './components/ConstructorsTab';
import SessionsTab from './components/SessionsTab/SessionsTab';
//import YearSelector from './components/YearSelector/YearSelector';
import { F1DataService } from './services/api/f1-data.service';
import { TabTypes } from './constants/common-constants';

const App: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(
    new Date().getFullYear()
  );
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [availableYears, setAvailableYears] = useState<
    { year: number; synced: boolean }[]
  >([]);
  const [isLoadingYears, setIsLoadingYears] = useState(true);

  // Fetch available years on mount
  React.useEffect(() => {
    const initialLoad = async () => {
      try {
        // Fetch available years
        const years = await F1DataService.getAvailableYears();
        setAvailableYears(years);

        // Check and sync data for the current year
        const currentYear = new Date().getFullYear();
        const syncStatus = await F1DataService.getSyncStatus(currentYear);
        let shouldSync = false;

        if (syncStatus.last_synced) {
          const lastSyncedDate = new Date(syncStatus.last_synced);
          const now = new Date();
          const oneHour = 60 * 60 * 1000; // 1 hour in milliseconds
          if (now.getTime() - lastSyncedDate.getTime() > oneHour) {
            shouldSync = true;
          }
        } else {
          shouldSync = true; // Sync if never synced before
        }

        if (shouldSync) {
          await F1DataService.syncData(currentYear);
          // Refresh years after sync
          const updatedYears = await F1DataService.getAvailableYears();
          setAvailableYears(updatedYears);
        }
      } catch (error) {
        console.error('Error during initial load and sync:', error);
      } finally {
        setIsLoadingYears(false);
      }
    };

    initialLoad();
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case TabTypes.OVERVIEW:
        return (
          <OverviewTab selectedYear={selectedYear} onTabChange={setActiveTab} />
        );
      case TabTypes.DRIVERS:
        return <DriversTab selectedYear={selectedYear} />;
      case TabTypes.CONSTRUCTORS:
        return <ConstructorsTab selectedYear={selectedYear} />;
      case TabTypes.SESSIONS:
        return <SessionsTab selectedYear={selectedYear} />;
      default:
        return null;
    }
  };

  return (
    <div className="app">
      {/* Year Selector
        <div className="app-header">
          <h1>F1 Statistics</h1>
          <YearSelector
            availableYears={availableYears}
            selectedYear={selectedYear}
            onYearChange={setSelectedYear}
            loading={isLoadingYears}
          />
        </div>
        */}
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="app-content">{renderContent()}</div>
    </div>
  );
};

export default App;
