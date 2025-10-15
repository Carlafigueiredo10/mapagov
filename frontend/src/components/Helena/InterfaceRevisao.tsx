import React from 'react';
import { Edit2, CheckCircle, AlertCircle } from 'lucide-react';

interface InterfaceRevisaoProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceRevisao: React.FC<InterfaceRevisaoProps> = ({ dados, onConfirm }) => {
  const dadosCompletos = (dados?.dados_completos as Record<string, unknown>) || {};
  const editavel = dados?.editavel !== false;

  const handleEditar = () => {
    onConfirm('editar');
  };

  const handleFinalizar = () => {
    onConfirm('finalizar');
  };

  // Helper para renderizar valor (array, objeto ou string)
  const renderizarValor = (valor: unknown): string => {
    if (!valor) return '(Não informado)';

    if (Array.isArray(valor)) {
      if (valor.length === 0) return '(Nenhum item)';
      return valor.map((item) => {
        if (typeof item === 'string') return `• ${item}`;
        if (typeof item === 'object') {
          // Fluxos de entrada/saída
          if (item.origem) return `• ${item.origem} → ${item.tipo || 'Sem tipo'}: ${item.descricao || ''}`;
          if (item.destino) return `• ${item.tipo || 'Sem tipo'} → ${item.destino}: ${item.descricao || ''}`;
          // Etapas
          if (item.numero) return `${item.numero}. ${item.descricao || ''}`;
          return `• ${JSON.stringify(item)}`;
        }
        return `• ${item}`;
      }).join('\n');
    }

    if (typeof valor === 'object') {
      const obj = valor as Record<string, unknown>;
      if (obj.nome && obj.codigo) return `${obj.nome} (${obj.codigo})`;
      return JSON.stringify(valor);
    }

    return String(valor);
  };

  // Estrutura de seções para exibição
  const secoes = [
    {
      titulo: '👤 Identificação',
      icone: '👤',
      campos: [
        { label: 'Mapeado por', key: 'nome_usuario' },
        { label: 'Código do Processo', key: 'codigo_processo' },
      ]
    },
    {
      titulo: '🏢 Localização Organizacional',
      icone: '🏢',
      campos: [
        { label: 'Área', key: 'area' },
        { label: 'Macroprocesso', key: 'macroprocesso' },
        { label: 'Processo', key: 'processo' },
        { label: 'Subprocesso', key: 'subprocesso' },
        { label: 'Atividade', key: 'atividade' },
      ]
    },
    {
      titulo: '📋 Descrição da Atividade',
      icone: '📋',
      campos: [
        { label: 'Nome da Atividade', key: 'nome_processo' },
        { label: 'Processo Específico', key: 'processo_especifico' },
        { label: 'Entrega Esperada', key: 'entrega_esperada' },
      ]
    },
    {
      titulo: '⚙️ Recursos e Sistemas',
      icone: '⚙️',
      campos: [
        { label: 'Sistemas Utilizados', key: 'sistemas' },
        { label: 'Documentos Necessários', key: 'documentos_utilizados' },
      ]
    },
    {
      titulo: '👥 Responsáveis e Normas',
      icone: '👥',
      campos: [
        { label: 'Operadores', key: 'operadores' },
        { label: 'Dispositivos Normativos', key: 'dispositivos_normativos' },
      ]
    },
    {
      titulo: '⚠️ Pontos de Atenção',
      icone: '⚠️',
      campos: [
        { label: 'Pontos de Atenção', key: 'pontos_atencao' },
      ]
    },
    {
      titulo: '🔄 Etapas do Processo',
      icone: '🔄',
      campos: [
        { label: 'Etapas', key: 'etapas' },
      ]
    },
    {
      titulo: '📥📤 Fluxos',
      icone: '🔀',
      campos: [
        { label: 'Fluxos de Entrada', key: 'fluxos_entrada' },
        { label: 'Fluxos de Saída', key: 'fluxos_saida' },
      ]
    },
  ];

  // Verificar completude
  const camposObrigatorios = ['nome_processo', 'entrega_esperada', 'area'];
  const camposFaltando = camposObrigatorios.filter(campo => !dadosCompletos[campo]);
  const completo = camposFaltando.length === 0;

  return (
    <div className="interface-revisao fade-in">
      <div className="revisao-header">
        <div className="revisao-title">
          <CheckCircle size={24} className="icon-success" />
          <h2>Revisão Final do POP</h2>
        </div>
        <p className="revisao-subtitle">
          Confira todos os dados antes de gerar o documento final
        </p>

        {!completo && (
          <div className="alerta-incompleto">
            <AlertCircle size={18} />
            <span>Alguns campos obrigatórios estão faltando. Clique em "Editar" para completar.</span>
          </div>
        )}
      </div>

      <div className="revisao-content">
        {secoes.map((secao, idx) => {
          return (
            <div key={idx} className="secao-revisao">
              <div className="secao-titulo">
                <span className="secao-icone">{secao.icone}</span>
                <h3>{secao.titulo}</h3>
              </div>

              <div className="secao-campos">
                {secao.campos.map((campo, cidx) => {
                  const valor = dadosCompletos[campo.key];
                  const temValor = valor && (
                    (Array.isArray(valor) && valor.length > 0) ||
                    (!Array.isArray(valor) && valor)
                  );

                  return (
                    <div key={cidx} className="campo-revisao">
                      <label className="campo-label">{campo.label}:</label>
                      <div className={`campo-valor ${!temValor ? 'campo-vazio' : ''}`}>
                        <pre>{renderizarValor(valor)}</pre>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="revisao-footer">
        {editavel && (
          <button
            onClick={handleEditar}
            className="btn-revisao btn-editar"
          >
            <Edit2 size={18} />
            Editar Campos
          </button>
        )}
        <button
          onClick={handleFinalizar}
          className="btn-revisao btn-finalizar"
          disabled={!completo}
        >
          <CheckCircle size={18} />
          {completo ? 'Finalizar e Gerar PDF' : 'Complete os campos obrigatórios'}
        </button>
      </div>

      <style>{`
        .interface-revisao {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          max-height: 70vh;
          overflow-y: auto;
        }

        .revisao-header {
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid #e9ecef;
        }

        .revisao-title {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.5rem;
        }

        .revisao-title h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #212529;
        }

        .icon-success {
          color: #28a745;
        }

        .revisao-subtitle {
          margin: 0;
          color: #6c757d;
          font-size: 0.95rem;
        }

        .alerta-incompleto {
          margin-top: 1rem;
          padding: 0.75rem 1rem;
          background: #fff3cd;
          border: 1px solid #ffc107;
          border-radius: 6px;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #856404;
          font-size: 0.9rem;
        }

        .revisao-content {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .secao-revisao {
          background: #f8f9fa;
          border-radius: 8px;
          padding: 1rem;
          border: 1px solid #dee2e6;
        }

        .secao-titulo {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 1rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid #dee2e6;
        }

        .secao-icone {
          font-size: 1.25rem;
        }

        .secao-titulo h3 {
          margin: 0;
          font-size: 1.1rem;
          color: #495057;
        }

        .secao-campos {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .campo-revisao {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .campo-label {
          font-size: 0.85rem;
          font-weight: 600;
          color: #495057;
        }

        .campo-valor {
          background: white;
          padding: 0.5rem;
          border-radius: 4px;
          border: 1px solid #ced4da;
          font-size: 0.9rem;
          color: #212529;
        }

        .campo-valor pre {
          margin: 0;
          font-family: inherit;
          white-space: pre-wrap;
          word-wrap: break-word;
        }

        .campo-vazio {
          background: #fff3cd;
          border-color: #ffc107;
          color: #856404;
          font-style: italic;
        }

        .revisao-footer {
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 2px solid #e9ecef;
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        .btn-revisao {
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

        .btn-editar {
          background: #6c757d;
          color: white;
        }

        .btn-editar:hover {
          background: #5a6268;
          transform: translateY(-1px);
        }

        .btn-finalizar {
          background: #28a745;
          color: white;
        }

        .btn-finalizar:hover:not(:disabled) {
          background: #218838;
          transform: translateY(-1px);
        }

        .btn-finalizar:disabled {
          background: #ced4da;
          color: #6c757d;
          cursor: not-allowed;
        }

        /* Scroll customizado */
        .interface-revisao::-webkit-scrollbar {
          width: 8px;
        }

        .interface-revisao::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 4px;
        }

        .interface-revisao::-webkit-scrollbar-thumb {
          background: #888;
          border-radius: 4px;
        }

        .interface-revisao::-webkit-scrollbar-thumb:hover {
          background: #555;
        }
      `}</style>
    </div>
  );
};

export default InterfaceRevisao;
