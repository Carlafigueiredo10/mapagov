/**
 * Button Component - Botões com variantes
 */
import React, { CSSProperties } from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
  style?: CSSProperties;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  style
}) => {
  const getVariantStyle = (): CSSProperties => {
    switch (variant) {
      case 'primary':
        return {
          background: '#1B4F72',
          color: '#ffffff',
          border: '2px solid #1B4F72'
        };
      case 'secondary':
        return {
          background: '#3498DB',
          color: '#ffffff',
          border: '2px solid #3498DB'
        };
      case 'outline':
        return {
          background: 'transparent',
          color: '#1B4F72',
          border: '2px solid #1B4F72'
        };
      case 'ghost':
        return {
          background: 'transparent',
          color: '#374151',
          border: 'none'
        };
      default:
        return {};
    }
  };

  const getSizeStyle = (): CSSProperties => {
    switch (size) {
      case 'sm':
        return { padding: '8px 16px', fontSize: '14px' };
      case 'lg':
        return { padding: '16px 32px', fontSize: '18px' };
      default:
        return { padding: '12px 24px', fontSize: '16px' };
    }
  };

  const baseStyle: CSSProperties = {
    borderRadius: '8px',
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease',
    opacity: disabled ? 0.5 : 1,
    ...getVariantStyle(),
    ...getSizeStyle(),
    ...style
  };

  return (
    <button
      className={className}
      style={baseStyle}
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {children}
    </button>
  );
};

export default Button;
