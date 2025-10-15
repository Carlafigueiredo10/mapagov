import React, { useState } from 'react';
import './ModalAjudaHelena.css';

interface ModalAjudaHelenaProps {
  nivelAtual: 'macro' | 'processo' | 'subprocesso' | 'atividade' | 'resultado';
  contextoJaSelecionado?: {
    macroprocesso?: string;
    processo?: string;
    subprocesso?: string;
    atividade?: string;
  };
  onFechar: () => void;
  onEnviar: (descricao: string) => void;
  carregando?: boolean;
}

const ModalAjudaHelena: React.FC<ModalAjudaHelenaProps> = ({
  nivelAtual,
  contextoJaSelecionado,
  onFechar,
  onEnviar,
  carregando = false,
}) => {
  const [descricao, setDescricao] = useState('');

  const titulosPorNivel = {
    macro: 'Conte-me sobre o que você faz',
    processo: 'Descreva o processo que você executa',
    subprocesso: 'Descreva o subprocesso específico',
    atividade: 'Descreva a atividade que você realiza',
    resultado: 'Descreva o resultado final que você entrega',
  };

  const placeholdersPorNivel = {
    macro: 'Ex: Trabalho com análise de aposentadorias, verificando documentos e requisitos...',
    processo: 'Ex: Eu analiso pedidos de aposentadoria e verifico se está tudo conforme...',
    subprocesso: 'Ex: Verifico os documentos enviados e analiso a conformidade...',
    atividade: 'Ex: Faço a validação dos tempos de contribuição no sistema...',
    resultado: 'Ex: Gero um parecer aprovando ou negando a aposentadoria...',
  };

  const handleEnviar = () => {
    if (!descricao.trim()) {
      alert('Por favor, descreva sua atividade para eu poder te ajudar!');
      return;
    }
    onEnviar(descricao.trim());
  };

  return (
    <div className="modal-ajuda-overlay" onClick={onFechar}>
      <div className="modal-ajuda-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-ajuda-header">
          <div className="modal-ajuda-avatar">
            <img src="/static/img/helena-avatar.png" alt="Helena" />
          </div>
          <div className="modal-ajuda-title">
            <h3>🆘 Preciso de Ajuda</h3>
            <p>{titulosPorNivel[nivelAtual]}</p>
          </div>
          <button className="modal-ajuda-fechar" onClick={onFechar}>
            ✕
          </button>
        </div>

        {contextoJaSelecionado && Object.keys(contextoJaSelecionado).length > 0 && (
          <div className="modal-ajuda-contexto">
            <p><strong>📌 Contexto já definido:</strong></p>
            {contextoJaSelecionado.macroprocesso && (
              <div className="contexto-item">
                <span className="contexto-label">Macroprocesso:</span>
                <span className="contexto-valor">{contextoJaSelecionado.macroprocesso}</span>
              </div>
            )}
            {contextoJaSelecionado.processo && (
              <div className="contexto-item">
                <span className="contexto-label">Processo:</span>
                <span className="contexto-valor">{contextoJaSelecionado.processo}</span>
              </div>
            )}
            {contextoJaSelecionado.subprocesso && (
              <div className="contexto-item">
                <span className="contexto-label">Subprocesso:</span>
                <span className="contexto-valor">{contextoJaSelecionado.subprocesso}</span>
              </div>
            )}
            {contextoJaSelecionado.atividade && (
              <div className="contexto-item">
                <span className="contexto-label">Atividade:</span>
                <span className="contexto-valor">{contextoJaSelecionado.atividade}</span>
              </div>
            )}
          </div>
        )}

        <div className="modal-ajuda-body">
          <label htmlFor="descricao-atividade">
            Descreva com suas palavras o que você faz:
          </label>
          <textarea
            id="descricao-atividade"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            placeholder={placeholdersPorNivel[nivelAtual]}
            rows={6}
            disabled={carregando}
            autoFocus
          />
          <p className="modal-ajuda-hint">
            💡 Quanto mais detalhes você der, melhor eu consigo te ajudar a classificar sua atividade!
          </p>
        </div>

        <div className="modal-ajuda-footer">
          <button className="btn-modal-cancelar" onClick={onFechar} disabled={carregando}>
            Cancelar
          </button>
          <button
            className="btn-modal-enviar"
            onClick={handleEnviar}
            disabled={carregando || !descricao.trim()}
          >
            {carregando ? '⏳ Analisando...' : '✨ Analisar com Helena'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalAjudaHelena;
