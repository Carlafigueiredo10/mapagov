import React, { useState, useEffect } from 'react';
import './TransitionLoadingState.css';

interface TransitionLoadingStateProps {
  title: string;
  subtitle: string;
  /** Skeleton variant: 'sugestao_entrega' matches the suggestion card layout */
  skeleton?: 'sugestao_entrega' | 'lista' | 'card';
  /** Seconds before showing extended wait message (default: 8) */
  timeoutSeconds?: number;
}

const TransitionLoadingState: React.FC<TransitionLoadingStateProps> = ({
  title,
  subtitle,
  skeleton = 'sugestao_entrega',
  timeoutSeconds = 8,
}) => {
  const [showExtended, setShowExtended] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowExtended(true), timeoutSeconds * 1000);
    return () => clearTimeout(timer);
  }, [timeoutSeconds]);

  return (
    <div className="transition-loading-container" role="status" aria-live="polite">
      {/* Contextual message */}
      <div className="transition-loading-header">
        <div className="transition-loading-spinner" aria-hidden="true" />
        <div className="transition-loading-text">
          <span className="transition-loading-title">{title}</span>
          <span className="transition-loading-subtitle">
            {showExtended
              ? `Ainda processando. ${subtitle}`
              : subtitle}
          </span>
        </div>
      </div>

      {/* Skeleton matching InterfaceSugestaoEntregaEsperada layout */}
      {skeleton === 'sugestao_entrega' && (
        <div className="transition-skeleton-card" aria-hidden="true">
          <div className="transition-skeleton-label" />
          <div className="transition-skeleton-value" />
          <div className="transition-skeleton-question" />
          <div className="transition-skeleton-buttons">
            <div className="transition-skeleton-btn transition-skeleton-btn-primary" />
            <div className="transition-skeleton-btn transition-skeleton-btn-secondary" />
          </div>
        </div>
      )}

      {skeleton === 'lista' && (
        <div className="transition-skeleton-card" aria-hidden="true">
          <div className="transition-skeleton-line" />
          <div className="transition-skeleton-line transition-skeleton-line-short" />
          <div className="transition-skeleton-line" />
        </div>
      )}

      {skeleton === 'card' && (
        <div className="transition-skeleton-card" aria-hidden="true">
          <div className="transition-skeleton-label" />
          <div className="transition-skeleton-value" />
        </div>
      )}
    </div>
  );
};

export default TransitionLoadingState;
