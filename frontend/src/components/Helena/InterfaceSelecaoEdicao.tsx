import React, { useState } from 'react';
import { Edit2, ChevronRight } from 'lucide-react';

interface CampoEditavel {
  campo: string;
  label: string;
}

interface InterfaceSelecaoEdicaoProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceSelecaoEdicao: React.FC<InterfaceSelecaoEdicaoProps> = ({ dados, onConfirm }) => {
  const [selecionado, setSelecionado] = useState<string | null>(null);

  // Campos editáveis conforme backend
  const camposEditaveis = dados?.campos_editaveis as Record<string, CampoEditavel> || {
    "1": { campo: "area", label: "Área da DECIPEX" },
    "2": { campo: "arquitetura", label: "Localização na arquitetura (Macro/Processo/Subprocesso/Atividade)" },
    "3": { campo: "sistemas", label: "Sistemas utilizados" },
    "4": { campo: "entrega_esperada", label: "Entrega esperada/Resultado final" },
    "5": { campo: "dispositivos_normativos", label: "Normas e dispositivos legais" },
    "6": { campo: "operadores", label: "Responsáveis pela execução" },
    "7": { campo: "pontos_atencao", label: "Pontos de atenção" },
    "8": { campo: "documentos_utilizados", label: "Documentos necessários" },
    "9": { campo: "etapas", label: "Etapas do processo" },
    "10": { campo: "fluxos", label: "Fluxos de entrada e saída" }
  };

  const handleSelect = (numero: string) => {
    setSelecionado(numero);
  };

  const handleConfirm = () => {
    if (!selecionado) {
      alert('Por favor, selecione um campo para editar');
      return;
    }
    onConfirm(selecionado);
  };

  const handleCancelar = () => {
    onConfirm('cancelar');
  };

  // Ícones por campo
  const iconesPorCampo: Record<string, string> = {
    "area": "🏢",
    "arquitetura": "🗂️",
    "sistemas": "⚙️",
    "entrega_esperada": "🎯",
    "dispositivos_normativos": "📜",
    "operadores": "👥",
    "pontos_atencao": "⚠️",
    "documentos_utilizados": "📄",
    "etapas": "🔄",
    "fluxos": "🔀"
  };

  return (
    <div className="interface-selecao-edicao fade-in">
      <div className="selecao-header">
        <div className="selecao-title">
          <Edit2 size={24} className="icon-edit" />
          <h2>Selecione o Campo para Editar</h2>
        </div>
        <p className="selecao-subtitle">
          Escolha qual informação você deseja modificar
        </p>
      </div>

      <div className="campos-lista">
        {Object.entries(camposEditaveis).map(([numero, campo]) => {
          const icone = iconesPorCampo[campo.campo] || "📝";
          const estaSelecionado = selecionado === numero;

          return (
            <button
              key={numero}
              onClick={() => handleSelect(numero)}
              className={`campo-item ${estaSelecionado ? 'selecionado' : ''}`}
            >
              <div className="campo-info">
                <span className="campo-icone">{icone}</span>
                <div className="campo-texto">
                  <span className="campo-numero">Campo {numero}</span>
                  <span className="campo-label">{campo.label}</span>
                </div>
              </div>
              <ChevronRight
                size={20}
                className={`campo-seta ${estaSelecionado ? 'ativa' : ''}`}
              />
            </button>
          );
        })}
      </div>

      <div className="selecao-footer">
        <button
          onClick={handleCancelar}
          className="btn-selecao btn-cancelar"
        >
          Cancelar
        </button>
        <button
          onClick={handleConfirm}
          className="btn-selecao btn-confirmar"
          disabled={!selecionado}
        >
          <Edit2 size={18} />
          Editar Campo Selecionado
        </button>
      </div>

      <style>{`
        .interface-selecao-edicao {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          max-height: 70vh;
          overflow-y: auto;
        }

        .selecao-header {
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid #e9ecef;
        }

        .selecao-title {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.5rem;
        }

        .selecao-title h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #212529;
        }

        .icon-edit {
          color: #007bff;
        }

        .selecao-subtitle {
          margin: 0;
          color: #6c757d;
          font-size: 0.95rem;
        }

        .campos-lista {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          margin-bottom: 1.5rem;
        }

        .campo-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem;
          background: #f8f9fa;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          text-align: left;
          width: 100%;
        }

        .campo-item:hover {
          background: #e9ecef;
          border-color: #adb5bd;
          transform: translateX(4px);
        }

        .campo-item.selecionado {
          background: #e7f3ff;
          border-color: #007bff;
          box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }

        .campo-info {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex: 1;
        }

        .campo-icone {
          font-size: 1.5rem;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 40px;
          height: 40px;
          background: white;
          border-radius: 8px;
        }

        .campo-texto {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .campo-numero {
          font-size: 0.75rem;
          font-weight: 600;
          color: #6c757d;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .campo-label {
          font-size: 0.95rem;
          font-weight: 500;
          color: #212529;
        }

        .campo-seta {
          color: #adb5bd;
          transition: all 0.2s;
        }

        .campo-seta.ativa {
          color: #007bff;
          transform: translateX(4px);
        }

        .selecao-footer {
          margin-top: 1.5rem;
          padding-top: 1rem;
          border-top: 2px solid #e9ecef;
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        .btn-selecao {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.95rem;
        }

        .btn-cancelar {
          background: #6c757d;
          color: white;
        }

        .btn-cancelar:hover {
          background: #5a6268;
          transform: translateY(-1px);
        }

        .btn-confirmar {
          background: #007bff;
          color: white;
        }

        .btn-confirmar:hover:not(:disabled) {
          background: #0056b3;
          transform: translateY(-1px);
        }

        .btn-confirmar:disabled {
          background: #ced4da;
          color: #6c757d;
          cursor: not-allowed;
        }

        /* Scroll customizado */
        .interface-selecao-edicao::-webkit-scrollbar {
          width: 8px;
        }

        .interface-selecao-edicao::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 4px;
        }

        .interface-selecao-edicao::-webkit-scrollbar-thumb {
          background: #888;
          border-radius: 4px;
        }

        .interface-selecao-edicao::-webkit-scrollbar-thumb:hover {
          background: #555;
        }
      `}</style>
    </div>
  );
};

export default InterfaceSelecaoEdicao;
