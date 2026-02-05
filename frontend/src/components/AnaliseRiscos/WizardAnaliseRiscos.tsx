/**
 * WizardAnaliseRiscos - Wizard de 6 etapas para Análise de Riscos v2
 *
 * Etapa 0: Selecao do tipo de objeto
 * Etapa 1: Contexto (Bloco A + B)
 * Etapa 2: Identificacao (6 blocos de perguntas)
 * Etapa 3: Analise (P x I)
 * Etapa 4: Matriz de Riscos
 * Etapa 5: Estrategias de Resposta
 */
import React, { useState, useEffect } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import Etapa0Entrada from './Etapa0_Entrada';
import Etapa1Contexto from './Etapa1_Contexto';
import Etapa2Blocos from './Etapa2_Blocos';
import Etapa3Analise from './Etapa3_Analise';
import Etapa4Matriz from './Etapa4_Matriz';
import Etapa5Resposta from './Etapa5_Resposta';

const ETAPAS = [
  { num: 0, nome: 'Entrada' },
  { num: 1, nome: 'Contexto' },
  { num: 2, nome: 'Identificacao' },
  { num: 3, nome: 'Analise' },
  { num: 4, nome: 'Matriz' },
  { num: 5, nome: 'Resposta' },
];

const WizardAnaliseRiscos: React.FC = () => {
  const [etapaAtual, setEtapaAtual] = useState(0);
  const [textoExtraidoPdf, setTextoExtraidoPdf] = useState('');

  const { loading, error, currentAnaliseId, currentAnalise, limparErro, resetStore } =
    useAnaliseRiscosStore();

  // Sincronizar etapa do wizard com etapa da analise
  useEffect(() => {
    if (currentAnalise?.etapa_atual !== undefined) {
      // etapa_atual do backend: 0=entrada, 1=contexto, 2=blocos
      // Se tiver riscos, mostra etapa 3
      if (currentAnalise.riscos?.length > 0) {
        setEtapaAtual(3);
      } else if (currentAnalise.etapa_atual >= 2) {
        setEtapaAtual(2);
      } else if (currentAnalise.etapa_atual >= 1) {
        setEtapaAtual(1);
      }
    }
  }, [currentAnalise?.etapa_atual, currentAnalise?.riscos?.length]);

  const avancar = () => {
    if (etapaAtual < 5) {
      setEtapaAtual(etapaAtual + 1);
    }
  };

  const voltar = () => {
    if (etapaAtual > 0) {
      setEtapaAtual(etapaAtual - 1);
    }
  };

  const handleNovaAnalise = () => {
    resetStore();
    setEtapaAtual(0);
  };

  const handleAvancarEtapa0 = (textoExtraido?: string) => {
    if (textoExtraido) {
      setTextoExtraidoPdf(textoExtraido);
    }
    avancar();
  };

  const [analiseFinalizada, setAnaliseFinalizada] = useState(false);

  const handleFinalizar = () => {
    setAnaliseFinalizada(true);
  };

  const handleExportar = (formato: 'pdf' | 'docx') => {
    if (!currentAnaliseId) return;
    const url = `/api/analise-riscos/${currentAnaliseId}/exportar/?formato=${formato}`;
    window.open(url, '_blank');
  };

  const renderEtapa = () => {
    if (analiseFinalizada) {
      return (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>✓</div>
          <h3 style={{ color: '#10b981' }}>Análise Finalizada com Sucesso!</h3>
          <p style={{ color: '#666', marginBottom: '30px' }}>
            A análise de riscos foi concluída e salva.
          </p>

          {/* Botões de Exportação */}
          <div style={{ marginBottom: '30px' }}>
            <p style={{ color: '#666', marginBottom: '15px', fontWeight: 'bold' }}>
              Exportar Relatório:
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '15px' }}>
              <button
                onClick={() => handleExportar('pdf')}
                style={{
                  padding: '12px 24px',
                  background: '#dc2626',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                }}
              >
                <span style={{ fontSize: '18px' }}>📄</span> Baixar PDF
              </button>
              <button
                onClick={() => handleExportar('docx')}
                style={{
                  padding: '12px 24px',
                  background: '#2563eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                }}
              >
                <span style={{ fontSize: '18px' }}>📝</span> Baixar Word
              </button>
            </div>
          </div>

          <button
            onClick={handleNovaAnalise}
            style={{
              padding: '12px 30px',
              background: '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Iniciar Nova Análise
          </button>
        </div>
      );
    }

    switch (etapaAtual) {
      case 0:
        return <Etapa0Entrada onAvancar={handleAvancarEtapa0} />;
      case 1:
        return <Etapa1Contexto onAvancar={avancar} onVoltar={voltar} textoExtraido={textoExtraidoPdf} />;
      case 2:
        return <Etapa2Blocos onAvancar={avancar} onVoltar={voltar} />;
      case 3:
        return <Etapa3Analise onAvancar={avancar} onVoltar={voltar} />;
      case 4:
        return <Etapa4Matriz onAvancar={avancar} onVoltar={voltar} />;
      case 5:
        return <Etapa5Resposta onVoltar={voltar} onFinalizar={handleFinalizar} />;
      default:
        return null;
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0 }}>Análise de Riscos</h2>
        {currentAnaliseId && (
          <button
            onClick={handleNovaAnalise}
            style={{
              padding: '8px 16px',
              background: '#f3f4f6',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Nova Análise
          </button>
        )}
      </div>

      {/* Stepper */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '20px',
          padding: '10px',
          background: '#f5f5f5',
          borderRadius: '8px',
        }}
      >
        {ETAPAS.map((etapa) => (
          <div
            key={etapa.num}
            style={{
              flex: 1,
              textAlign: 'center',
              padding: '10px',
              background: etapaAtual === etapa.num ? '#3b82f6' : etapaAtual > etapa.num ? '#10b981' : 'transparent',
              color: etapaAtual >= etapa.num ? 'white' : '#666',
              borderRadius: '4px',
              fontWeight: etapaAtual === etapa.num ? 'bold' : 'normal',
            }}
          >
            {etapa.nome}
          </div>
        ))}
      </div>

      {/* Info da analise */}
      {currentAnaliseId && (
        <div
          style={{
            padding: '12px 16px',
            background: '#f8f9fa',
            border: '1px solid #e6e6e6',
            borderRadius: '4px',
            marginBottom: '15px',
            fontSize: '14px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
            {currentAnalise?.tipo_origem && (
              <span>
                <span style={{ color: '#636363' }}>Objeto:</span>{' '}
                <strong style={{ color: '#333' }}>{currentAnalise.tipo_origem}</strong>
              </span>
            )}
            <span>
              <span style={{ color: '#636363' }}>ID:</span>{' '}
              <span style={{ fontFamily: 'monospace', color: '#333' }}>{currentAnaliseId.slice(0, 8)}</span>
            </span>
            {currentAnalise?.status && (
              <span>
                <span style={{ color: '#636363' }}>Status:</span>{' '}
                <span style={{ color: currentAnalise.status === 'RASCUNHO' ? '#b45309' : '#166534' }}>
                  {currentAnalise.status}
                </span>
              </span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {currentAnalise?.riscos?.length ? (
              <span style={{ color: '#1351B4', fontWeight: '600' }}>
                {currentAnalise.riscos.length} risco(s)
              </span>
            ) : null}
            <span style={{ color: '#636363', fontSize: '13px' }}>
              Etapa {etapaAtual + 1} de 6
            </span>
          </div>
        </div>
      )}

      {/* Erro */}
      {error && (
        <div
          style={{
            padding: '10px',
            background: '#fee2e2',
            color: '#dc2626',
            borderRadius: '4px',
            marginBottom: '15px',
          }}
        >
          Erro: {error.erro}
          {error.codigo && ` (${error.codigo})`}
          <button
            onClick={limparErro}
            style={{
              marginLeft: '10px',
              padding: '2px 8px',
              cursor: 'pointer',
            }}
          >
            Fechar
          </button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
          Carregando...
        </div>
      )}

      {/* Conteudo da etapa */}
      {!loading && renderEtapa()}
    </div>
  );
};

export default WizardAnaliseRiscos;
