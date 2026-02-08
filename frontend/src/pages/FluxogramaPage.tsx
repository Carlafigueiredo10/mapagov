/**
 * FluxogramaPage - Página dedicada para o Gerador de Fluxogramas
 *
 * Rota: /fluxograma
 *
 * Fluxo:
 * 1. Exibe landing institucional (enquadramento)
 * 2. Ao clicar em "Iniciar geração de fluxograma", exibe a ferramenta
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import LandingShell from '../components/ui/LandingShell';
import FluxogramaLanding from '../components/Fluxograma/FluxogramaLanding';
import FluxogramaUpload from '../components/Fluxograma/FluxogramaUpload';
import FluxogramaChat from '../components/Fluxograma/FluxogramaChat';
import FluxogramaPreview from '../components/Fluxograma/FluxogramaPreview';
import './FluxogramaPage.css';

interface POPInfo {
  atividade?: string;
  objetivo?: string;
  operadores?: string[];
  sistemas?: string[];
  etapas?: string[];
  documentos?: string[];
}

export default function FluxogramaPage() {
  const navigate = useNavigate();
  const [mostrarFerramenta, setMostrarFerramenta] = useState(false);
  const [pdfAnalyzed, setPdfAnalyzed] = useState(false);
  const [popInfo, setPopInfo] = useState<POPInfo | null>(null);
  const [fluxogramaCode, setFluxogramaCode] = useState<string>('');
  const [conversaCompleta, setConversaCompleta] = useState(false);

  const handlePdfAnalyzed = (info: POPInfo) => {
    setPopInfo(info);
    setPdfAnalyzed(true);
  };

  const handleFluxogramaGenerated = (code: string) => {
    setFluxogramaCode(code);
    setConversaCompleta(true);
  };

  // Landing institucional
  if (!mostrarFerramenta) {
    return (
      <LandingShell onBack={() => navigate(-1)}>
        <FluxogramaLanding onIniciar={() => setMostrarFerramenta(true)} />
      </LandingShell>
    );
  }

  // Ferramenta de geração
  return (
    <Layout>
      <div className="fluxograma-page">
        <div className="fluxograma-header">
          <h1>Gerador de Fluxogramas</h1>
          <p>Upload de PDF do POP e geração de fluxograma visual</p>
        </div>

        <div className="fluxograma-grid">
          {/* Coluna 1: Upload */}
          <div className="fluxograma-card">
            <div className="card-header">
              <h2>1. Upload do POP</h2>
              <p>Faça upload do PDF do seu Procedimento Operacional Padrão</p>
            </div>
            <div className="card-body">
              <FluxogramaUpload onPdfAnalyzed={handlePdfAnalyzed} />
            </div>
          </div>

          {/* Coluna 2: Chat */}
          <div className="fluxograma-card">
            <div className="card-header">
              <h2>2. Conversa com Helena</h2>
              <p>Helena vai fazer perguntas complementares sobre o processo</p>
            </div>
            <div className="card-body">
              <FluxogramaChat
                enabled={pdfAnalyzed}
                popInfo={popInfo}
                onFluxogramaGenerated={handleFluxogramaGenerated}
              />
            </div>
          </div>
        </div>

        {/* Preview do Fluxograma */}
        <div className="fluxograma-card fluxograma-full-width">
          <div className="card-header">
            <h2>3. Fluxograma Gerado</h2>
            <p>Visualização do fluxograma em formato Mermaid</p>
          </div>
          <div className="card-body">
            <FluxogramaPreview
              code={fluxogramaCode}
              isEmpty={!conversaCompleta}
            />
          </div>
        </div>
      </div>
    </Layout>
  );
}
