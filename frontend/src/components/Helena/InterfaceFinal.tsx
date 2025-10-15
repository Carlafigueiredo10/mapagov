import React, { useEffect, useState } from 'react';
import { CheckCircle, Download, FileText, Loader } from 'lucide-react';

interface InterfaceFinalProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceFinal: React.FC<InterfaceFinalProps> = ({ dados, onConfirm }) => {
  const [etapa, setEtapa] = useState<'processando' | 'sucesso' | 'erro'>('processando');
  const [mensagem, setMensagem] = useState('Preparando dados do POP...');
  const [pdfUrl] = useState<string | null>(null);

  const popCompleto = (dados?.pop_completo as Record<string, unknown>) || {};
  const codigo = dados?.codigo as string || 'POP-000';

  useEffect(() => {
    // Simular processamento (aqui vai chamar a API de PDF real)
    const timer = setTimeout(() => {
      setEtapa('sucesso');
      setMensagem('POP criado com sucesso!');
      // setPdfUrl será definido pela integração real com a API
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleBaixarPDF = () => {
    if (pdfUrl) {
      window.open(pdfUrl, '_blank');
    } else {
      // Se não tiver URL ainda, notificar (será usado na integração real)
      alert('Gerando PDF... aguarde um momento.');
    }
  };

  const handleNovoMapeamento = () => {
    onConfirm('novo_mapeamento');
  };

  return (
    <div className="interface-final fade-in">
      {etapa === 'processando' && (
        <div className="final-processando">
          <Loader size={48} className="icon-loading" />
          <h2>Finalizando POP...</h2>
          <p>{mensagem}</p>
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
        </div>
      )}

      {etapa === 'sucesso' && (
        <div className="final-sucesso">
          <div className="sucesso-icon-container">
            <CheckCircle size={64} className="icon-sucesso" />
          </div>

          <h2 className="sucesso-titulo">POP Criado com Sucesso!</h2>
          <p className="sucesso-subtitulo">
            Seu Procedimento Operacional Padrão está pronto
          </p>

          <div className="pop-resumo">
            <div className="resumo-header">
              <FileText size={24} />
              <h3>Resumo do Documento</h3>
            </div>

            <div className="resumo-detalhes">
              <div className="detalhe-item">
                <span className="detalhe-label">Código:</span>
                <span className="detalhe-valor">{codigo}</span>
              </div>
              <div className="detalhe-item">
                <span className="detalhe-label">Atividade:</span>
                <span className="detalhe-valor">{String(popCompleto.nome_processo || '(Não informado)')}</span>
              </div>
              <div className="detalhe-item">
                <span className="detalhe-label">Área:</span>
                <span className="detalhe-valor">
                  {String((popCompleto.area as { nome?: string })?.nome || popCompleto.area || '(Não informado)')}
                </span>
              </div>
              <div className="detalhe-item">
                <span className="detalhe-label">Etapas:</span>
                <span className="detalhe-valor">
                  {Array.isArray(popCompleto.etapas) ? popCompleto.etapas.length : 0} etapas
                </span>
              </div>
              <div className="detalhe-item">
                <span className="detalhe-label">Criado por:</span>
                <span className="detalhe-valor">{String(popCompleto.nome_usuario || 'Usuário')}</span>
              </div>
            </div>
          </div>

          <div className="acoes-final">
            <button
              onClick={handleBaixarPDF}
              className="btn-final btn-pdf"
              disabled={!pdfUrl}
            >
              <Download size={20} />
              {pdfUrl ? 'Baixar PDF' : 'Preparando PDF...'}
            </button>

            <button
              onClick={handleNovoMapeamento}
              className="btn-final btn-novo"
            >
              Iniciar Novo Mapeamento
            </button>
          </div>

          <div className="dica-final">
            💡 <strong>Dica:</strong> O PDF gerado pode ser editado posteriormente no Microsoft Word ou Google Docs.
          </div>
        </div>
      )}

      {etapa === 'erro' && (
        <div className="final-erro">
          <div className="erro-icon-container">
            <FileText size={64} className="icon-erro" />
          </div>
          <h2>Não foi possível gerar o PDF</h2>
          <p>Mas não se preocupe! Seus dados foram salvos.</p>
          <button onClick={handleNovoMapeamento} className="btn-final btn-novo">
            Tentar Novamente
          </button>
        </div>
      )}

      <style>{`
        .interface-final {
          background: white;
          border-radius: 12px;
          padding: 3rem 2rem;
          text-align: center;
          min-height: 400px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        /* Processando */
        .final-processando {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .icon-loading {
          color: #007bff;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .final-processando h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #212529;
        }

        .final-processando p {
          margin: 0;
          color: #6c757d;
        }

        .progress-bar {
          width: 300px;
          height: 4px;
          background: #e9ecef;
          border-radius: 2px;
          overflow: hidden;
          margin-top: 1rem;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #007bff, #0056b3);
          animation: progress 2s ease-in-out infinite;
        }

        @keyframes progress {
          0% { width: 0%; }
          50% { width: 70%; }
          100% { width: 100%; }
        }

        /* Sucesso */
        .final-sucesso {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.5rem;
          width: 100%;
          max-width: 600px;
        }

        .sucesso-icon-container {
          animation: scaleIn 0.5s ease-out;
        }

        @keyframes scaleIn {
          from {
            transform: scale(0);
            opacity: 0;
          }
          to {
            transform: scale(1);
            opacity: 1;
          }
        }

        .icon-sucesso {
          color: #28a745;
        }

        .sucesso-titulo {
          margin: 0;
          font-size: 2rem;
          color: #212529;
          font-weight: 700;
        }

        .sucesso-subtitulo {
          margin: 0;
          color: #6c757d;
          font-size: 1.1rem;
        }

        /* Resumo */
        .pop-resumo {
          width: 100%;
          background: #f8f9fa;
          border-radius: 8px;
          padding: 1.5rem;
          border: 1px solid #dee2e6;
        }

        .resumo-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1rem;
          padding-bottom: 0.75rem;
          border-bottom: 2px solid #dee2e6;
          color: #495057;
        }

        .resumo-header h3 {
          margin: 0;
          font-size: 1.1rem;
        }

        .resumo-detalhes {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .detalhe-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.5rem 0;
        }

        .detalhe-label {
          font-weight: 600;
          color: #495057;
          font-size: 0.9rem;
        }

        .detalhe-valor {
          color: #212529;
          font-size: 0.9rem;
          text-align: right;
          max-width: 60%;
        }

        /* Ações */
        .acoes-final {
          width: 100%;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .btn-final {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          padding: 1rem 2rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-pdf {
          background: #28a745;
          color: white;
        }

        .btn-pdf:hover:not(:disabled) {
          background: #218838;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        }

        .btn-pdf:disabled {
          background: #ced4da;
          color: #6c757d;
          cursor: not-allowed;
        }

        .btn-novo {
          background: #007bff;
          color: white;
        }

        .btn-novo:hover {
          background: #0056b3;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        }

        .dica-final {
          width: 100%;
          padding: 1rem;
          background: #fff3cd;
          border: 1px solid #ffc107;
          border-radius: 6px;
          color: #856404;
          font-size: 0.9rem;
          text-align: left;
        }

        /* Erro */
        .final-erro {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .erro-icon-container {
          animation: shake 0.5s;
        }

        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-10px); }
          75% { transform: translateX(10px); }
        }

        .icon-erro {
          color: #dc3545;
        }

        .final-erro h2 {
          margin: 0;
          color: #dc3545;
        }

        .final-erro p {
          margin: 0;
          color: #6c757d;
        }
      `}</style>
    </div>
  );
};

export default InterfaceFinal;
