/**
 * Badge Component - Tags e badges
 */
import React, { CSSProperties } from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'info' | 'outline';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className = ''
}) => {
  const getVariantStyle = (): CSSProperties => {
    switch (variant) {
      case 'success':
        return { background: '#10b981', color: '#ffffff' };
      case 'warning':
        return { background: '#f59e0b', color: '#ffffff' };
      case 'info':
        return { background: '#3b82f6', color: '#ffffff' };
      case 'outline':
        return {
          background: 'transparent',
          color: '#ffffff',
          border: '1px solid rgba(255, 255, 255, 0.4)'
        };
      default:
        return { background: '#6b7280', color: '#ffffff' };
    }
  };

  const baseStyle: CSSProperties = {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '9999px',
    fontSize: '12px',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    ...getVariantStyle()
  };

  return (
    <span className={className} style={baseStyle}>
      {children}
    </span>
  );
};

export default Badge;
