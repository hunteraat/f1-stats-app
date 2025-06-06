import React from 'react';
import './YearSelector.css';

interface YearInfo {
  year: number;
  synced: boolean;
}

interface YearSelectorProps {
  availableYears: YearInfo[];
  selectedYear: number;
  onYearChange: (year: number) => void;
  loading: boolean;
}

const YearSelector: React.FC<YearSelectorProps> = ({
  availableYears,
  selectedYear,
  onYearChange,
  loading,
}) => {
  return (
    <div className="year-selector">
      <label htmlFor="year-select">
        <span className="year-label">F1 Season: </span>
        <select
          id="year-select"
          value={selectedYear}
          onChange={e => onYearChange(parseInt(e.target.value))}
          disabled={loading}
          className="year-select"
        >
          {availableYears
            .filter(year => year.year >= 2018) // Focus on recent years with better data
            .sort((a, b) => b.year - a.year) // Sort newest first
            .map(yearInfo => (
              <option key={yearInfo.year} value={yearInfo.year}>
                {yearInfo.year}
              </option>
            ))}
        </select>
      </label>
    </div>
  );
};

export default YearSelector;
