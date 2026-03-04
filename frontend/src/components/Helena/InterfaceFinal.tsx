import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, FileText, Loader, Award } from 'lucide-react';

interface InterfaceFinalProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceFinal: React.FC<InterfaceFinalProps> = ({ dados }) => {
  const navigate = useNavigate();
  const [etapa, setEtapa] = useState<'processando' | 'sucesso' | 'erro'>('processando');

  const popCompleto = (dados?.pop_completo as Record<string, unknown>) || {};
  const codigo = dados?.codigo as string || 'POP-000';
  // pdfUrl vem dos dados da interface (atualizado pelo useChat após geração)
  const pdfUrl = (dados?.pdfUrl as string) || null;

  useEffect(() => {
    // Transição automática para sucesso após breve loading
    const timer = setTimeout(() => {
      setEtapa('sucesso');
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  // Se pdfUrl chegar depois (atualização do useChat), já mostra sucesso
  useEffect(() => {
    if (pdfUrl) setEtapa('sucesso');
  }, [pdfUrl]);


  return (
    <div className="interface-final fade-in">
      {etapa === 'processando' && (
        <div className="final-processando">
          <Loader size={48} className="icon-loading" />
          <h2>Finalizando POP...</h2>
          <p>Preparando dados do POP...</p>
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

          <h2 className="sucesso-titulo">POP salvo com sucesso!</h2>
          <p className="sucesso-subtitulo">
            Seu POP foi salvo como rascunho. Submeta para homologacao na pagina de mapeamento quando estiver pronto.
          </p>

          <div className="pop-resumo">
            <div className="resumo-header">
              <FileText size={24} />
              <h3>Resumo do Documento</h3>
            </div>

            <div className="resumo-detalhes">
              <div className="detalhe-item">
                <span className="detalhe-label">Codigo:</span>
                <span className="detalhe-valor">{codigo}</span>
              </div>
              <div className="detalhe-item">
                <span className="detalhe-label">Atividade:</span>
                <span className="detalhe-valor">{String(popCompleto.nome_processo || '(Nao informado)')}</span>
              </div>
              <div className="detalhe-item">
                <span className="detalhe-label">Area:</span>
                <span className="detalhe-valor">
                  {String((popCompleto.area as { nome?: string })?.nome || popCompleto.area || '(Nao informado)')}
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
                <span className="detalhe-valor">{String(popCompleto.nome_usuario || 'Usuario')}</span>
              </div>
            </div>
          </div>

          <div className="acoes-final">
            <button
              onClick={() => navigate('/pop/meus')}
              className="btn-final btn-pdf"
            >
              <FileText size={20} />
              Ir para Meus POPs
            </button>
          </div>

          <button
            type="button"
            className="badge-cartografo"
            onClick={() => navigate('/pop/meus')}
            role="link"
            aria-label="Ir para pagina de mapeamento"
          >
            <Award size={32} className="badge-icon" />
            <span className="badge-titulo">Cartografo do Conhecimento</span>
            <span className="badge-texto">Obrigada por contribuir com um processo mais padronizado e seguro.</span>
          </button>
        </div>
      )}

      {etapa === 'erro' && (
        <div className="final-erro">
          <div className="erro-icon-container">
            <FileText size={64} className="icon-erro" />
          </div>
          <h2>Não foi possível gerar o PDF</h2>
          <p>Mas não se preocupe! Seus dados foram salvos.</p>
          <button onClick={() => navigate('/pop/meus')} className="btn-final btn-novo">
            Voltar ao mapeamento
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

        /* Badge Cartografo */
        .badge-cartografo {
          width: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
          padding: 1.5rem;
          background: linear-gradient(135deg, #F0F4FA 0%, #E8F0FE 100%);
          border: 2px solid #1351B4;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s;
          text-align: center;
        }

        .badge-cartografo:hover {
          background: linear-gradient(135deg, #E8F0FE 0%, #D6E4F9 100%);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(19, 81, 180, 0.2);
        }

        .badge-icon {
          color: #1351B4;
        }

        .badge-titulo {
          font-size: 1.1rem;
          font-weight: 700;
          color: #1351B4;
        }

        .badge-texto {
          font-size: 0.85rem;
          color: #495057;
          line-height: 1.4;
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
