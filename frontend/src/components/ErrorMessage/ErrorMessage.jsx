import React from 'react';
import './ErrorMessage.css';

const ErrorMessage = ({ error, onDismiss }) => {
  if (!error) return null;

  return (
    <div className="error-message">
      <div className="error-content">
        <span className="error-icon">⚠️</span>
        <span className="error-text">{error}</span>
      </div>
      {onDismiss && (
        <button className="dismiss-button" onClick={onDismiss}>
          ✕
        </button>
      )}
    </div>
  );
};

export default ErrorMessage; 