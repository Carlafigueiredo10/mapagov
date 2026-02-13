import React from 'react';

interface LoadingAnaliseAtividadeProps {
  onEntendi?: () => void;
}

const LoadingAnaliseAtividade: React.FC<LoadingAnaliseAtividadeProps> = ({ onEntendi }) => {
  return (
    <div className="explicacao-classificacao-container">
      <h3 className="explicacao-titulo">Entenda como sua atividade é classificada</h3>

      <p className="explicacao-intro">
        Enquanto buscamos sua atividade, é importante esclarecer como funciona a organização do trabalho no sistema.
      </p>

      <div className="explicacao-conceito">
        <strong>Área organizacional</strong> é a unidade onde você está lotado(a).
        <br />
        <span className="explicacao-exemplo-inline">Exemplo: CGBEN, COATE, CGRIS.</span>
      </div>

      <div className="explicacao-conceito">
        <strong>Macroprocesso</strong> é a classificação transversal do tipo de trabalho executado, independentemente da área.
      </div>

      <p className="explicacao-destaque">
        Ou seja, a classificação não considera apenas onde você trabalha, mas <strong>qual é a natureza da atividade</strong>.
      </p>

      <div className="explicacao-exemplo-bloco">
        <strong>Exemplo:</strong> Se você atua na <strong>COATE</strong> mas trabalha com demanda judicial, seu macroprocesso será <strong>Gestão de Demandas Judiciais</strong>, mesmo que esse macroprocesso seja típico da CGRIS.
      </div>

      {onEntendi && (
        <button className="explicacao-btn-entendi" onClick={onEntendi}>
          Entendi
        </button>
      )}

      <style>{`
        .explicacao-classificacao-container {
          padding: 24px;
          background: #ffffff;
          border: 1px solid #d4d4d4;
          border-left: 4px solid #1351B4;
          border-radius: 8px;
          max-width: 600px;
          margin: 16px auto;
          color: #333333;
          font-size: 15px;
          line-height: 1.6;
        }

        .explicacao-titulo {
          margin: 0 0 16px 0;
          font-size: 18px;
          font-weight: 600;
          color: #1B4F72;
        }

        .explicacao-intro {
          margin: 0 0 16px 0;
          color: #555555;
        }

        .explicacao-conceito {
          margin: 0 0 12px 0;
          padding: 12px;
          background: #f5f8fc;
          border-radius: 6px;
        }

        .explicacao-conceito strong {
          color: #1351B4;
        }

        .explicacao-exemplo-inline {
          color: #777777;
          font-size: 14px;
        }

        .explicacao-destaque {
          margin: 16px 0;
          font-size: 14px;
          color: #555555;
        }

        .explicacao-exemplo-bloco {
          margin: 0 0 20px 0;
          padding: 14px;
          background: #fffbea;
          border: 1px solid #f0e6c0;
          border-radius: 6px;
          font-size: 14px;
          color: #555555;
        }

        .explicacao-exemplo-bloco strong {
          color: #333333;
        }

        .explicacao-btn-entendi {
          display: block;
          width: 100%;
          padding: 12px;
          background: #1351B4;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }

        .explicacao-btn-entendi:hover {
          background: #0d3d8a;
        }
      `}</style>
    </div>
  );
};

export default LoadingAnaliseAtividade;
