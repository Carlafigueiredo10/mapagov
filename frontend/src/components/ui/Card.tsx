/**
 * Card Component - Base para containers com glassmorphism
 */
import React, { CSSProperties } from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glass' | 'solid';
  onClick?: () => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  style?: CSSProperties;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'default',
  onClick,
  onMouseEnter,
  onMouseLeave,
  style
}) => {
  const getVariantStyle = (): CSSProperties => {
    switch (variant) {
      case 'glass':
        return {
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(27, 79, 114, 0.15)',
          boxShadow: '0 8px 32px 0 rgba(27, 79, 114, 0.15)'
        };
      case 'solid':
        return {
          background: '#ffffff',
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        };
      default:
        return {
          background: '#ffffff',
          border: '1px solid #e5e7eb',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        };
    }
  };

  const baseStyle: CSSProperties = {
    borderRadius: '16px',
    padding: '24px',
    transition: 'all 0.3s ease',
    cursor: onClick ? 'pointer' : 'default',
    ...getVariantStyle(),
    ...style
  };

  return (
    <div
      className={className}
      style={baseStyle}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {children}
    </div>
  );
};

export default Card;
