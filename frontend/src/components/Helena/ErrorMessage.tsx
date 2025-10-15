import React from 'react';
import { AlertCircle, X } from 'lucide-react';
import './ErrorMessage.css';

interface ErrorMessageProps {
  message: string;
  onClose: () => void;
  type?: 'error' | 'warning' | 'info';
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  message, 
  onClose, 
  type = 'error' 
}) => {
  return (
    <div className={`error-message ${type}`}>
      <div className="error-content">
        <AlertCircle size={20} />
        <span className="error-text">{message}</span>
      </div>
      <button 
        className="error-close"
        onClick={onClose}
        title="Fechar"
      >
        <X size={16} />
      </button>
    </div>
  );
};

export default ErrorMessage;