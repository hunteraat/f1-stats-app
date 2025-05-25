import React from 'react';

const ErrorMessage = ({ error, onDismiss }) => {
  if (!error) return null;

  return (
    <div className="error-message">
      <div className="error-content">
        <span className="error-icon">⚠️</span>
        <span className="error-text">{error}</span>
      </div>
      <button onClick={onDismiss} className="error-dismiss">
        ✕
      </button>
    </div>
  );
};

export default ErrorMessage;