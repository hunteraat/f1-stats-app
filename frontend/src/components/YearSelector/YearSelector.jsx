import React from 'react';
import './YearSelector.css';

const YearSelector = ({ availableYears, selectedYear, onYearChange, loading }) => {
  return (
    <div className="year-selector">
      <label htmlFor="year-select">
        <span className="year-label">Select F1 Season: </span>
        <select 
          id="year-select"
          value={selectedYear} 
          onChange={(e) => onYearChange(parseInt(e.target.value))}
          disabled={loading}
          className="year-select"
        >
          {availableYears
            .filter(year => year.year >= 2018) // Focus on recent years with better data
            .sort((a, b) => b.year - a.year) // Sort newest first
            .map(yearInfo => (
              <option key={yearInfo.year} value={yearInfo.year}>
                {yearInfo.year} {yearInfo.synced ? '✅' : '⏳'} 
                {yearInfo.synced && yearInfo.drivers_count > 0 
                  ? ` (${yearInfo.drivers_count} drivers)` 
                  : ''
                }
              </option>
            ))
          }
        </select>
      </label>
    </div>
  );
};

export default YearSelector; 