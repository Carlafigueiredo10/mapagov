import React from 'react';

interface InterfaceFallbackProps {
  tipo: string;
  errors?: string[];
  schemaVersion?: string;
}

const InterfaceFallback: React.FC<InterfaceFallbackProps> = ({ tipo, errors, schemaVersion }) => {
  const isDev = import.meta.env.DEV;

  return (
    <div style={{
      border: '2px dashed #e6a817',
      borderRadius: '8px',
      padding: '16px',
      margin: '8px 0',
      backgroundColor: '#fffbe6',
      color: '#5c4813',
      fontSize: '14px',
    }}>
      <p style={{ margin: 0, fontWeight: 600 }}>
        Interface temporariamente indisponivel
      </p>
      <p style={{ margin: '4px 0 0', fontSize: '13px', opacity: 0.8 }}>
        Tipo: {tipo}{schemaVersion ? ` (v${schemaVersion})` : ''}
      </p>
      {isDev && errors && errors.length > 0 && (
        <details style={{ marginTop: '8px', fontSize: '12px' }}>
          <summary style={{ cursor: 'pointer' }}>Erros de validacao</summary>
          <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
            {errors.map((err, i) => <li key={i}>{err}</li>)}
          </ul>
        </details>
      )}
    </div>
  );
};

export default InterfaceFallback;
