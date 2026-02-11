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
import { useRequireAuth } from '../hooks/useRequireAuth';
import FluxogramaUpload from '../components/Fluxograma/FluxogramaUpload';
import FluxogramaChat from '../components/Fluxograma/FluxogramaChat';
import FluxogramaPreview from '../components/Fluxograma/FluxogramaPreview';
import StepList from '../components/Fluxograma/StepList';
import StepEditModal from '../components/Fluxograma/StepEditModal';
import api from '../services/api';
import './FluxogramaPage.css';

interface POPInfo {
  atividade?: string;
  objetivo?: string;
  operadores?: string[];
  sistemas?: string[];
  etapas?: string[];
  documentos?: string[];
}

interface FlowStep {
  id: number;
  label: string;
  texto: string;
}

interface FlowDecision {
  id: number;
  apos_etapa_id: number;
  condicao: string;
  sim_id: number;
  nao_id: number;
}

export default function FluxogramaPage() {
  const navigate = useNavigate();
  const requireAuth = useRequireAuth();
  const [mostrarFerramenta, setMostrarFerramenta] = useState(false);
  const [pdfAnalyzed, setPdfAnalyzed] = useState(false);
  const [popInfo, setPopInfo] = useState<POPInfo | null>(null);
  const [fluxogramaCode, setFluxogramaCode] = useState<string>('');
  const [conversaCompleta, setConversaCompleta] = useState(false);

  // Step editing state
  const [steps, setSteps] = useState<FlowStep[]>([]);
  const [decisoes, setDecisoes] = useState<FlowDecision[]>([]);
  const [activeStepId, setActiveStepId] = useState<number | null>(null);
  const [editingStep, setEditingStep] = useState<FlowStep | null>(null);
  const [modalMode, setModalMode] = useState<'edit' | 'insert'>('edit');
  const [insertAfterId, setInsertAfterId] = useState<number | null>(null);
  const [stepError, setStepError] = useState<string | null>(null);

  const handlePdfAnalyzed = (info: POPInfo) => {
    setPopInfo(info);
    setPdfAnalyzed(true);
  };

  const handleFluxogramaGenerated = (code: string, responseSteps?: FlowStep[], responseDecisoes?: FlowDecision[]) => {
    setFluxogramaCode(code);
    setConversaCompleta(true);
    if (responseSteps) setSteps(responseSteps);
    if (responseDecisoes) setDecisoes(responseDecisoes);
  };

  // --- Step manipulation handlers ---

  const handleInsertAfter = (afterId: number) => {
    const afterStep = steps.find((s) => s.id === afterId);
    setInsertAfterId(afterId);
    setEditingStep(afterStep || null);
    setModalMode('insert');
    setStepError(null);
  };

  const handleEditOpen = (stepId: number) => {
    const step = steps.find((s) => s.id === stepId);
    if (step) {
      setEditingStep(step);
      setModalMode('edit');
      setStepError(null);
    }
  };

  const handleModalSave = async (stepId: number | null, texto: string) => {
    try {
      setStepError(null);
      let payload: any;

      if (modalMode === 'insert') {
        payload = { action: 'insert_after', after_step_id: insertAfterId, texto };
      } else {
        payload = { action: 'edit', step_id: stepId, texto };
      }

      const response = await api.post('/fluxograma-steps/', payload);
      const data = response.data;

      if (!data.ok) {
        setStepError(data.mensagem || 'Erro ao salvar etapa.');
        return;
      }

      setSteps(data.steps);
      setDecisoes(data.decisoes || []);
      setFluxogramaCode(data.fluxograma_mermaid);
      setActiveStepId(data.new_step_id || null);
      setEditingStep(null);
      setInsertAfterId(null);
    } catch (err: any) {
      const msg = err?.response?.data?.mensagem || 'Erro de conexão.';
      setStepError(msg);
    }
  };

  const handleRemoveStep = async (stepId: number) => {
    try {
      setStepError(null);
      const response = await api.post('/fluxograma-steps/', {
        action: 'remove',
        step_id: stepId,
      });
      const data = response.data;

      if (!data.ok) {
        setStepError(data.mensagem || 'Erro ao remover etapa.');
        return;
      }

      setSteps(data.steps);
      setDecisoes(data.decisoes || []);
      setFluxogramaCode(data.fluxograma_mermaid);
      setActiveStepId(null);
      setEditingStep(null);
    } catch (err: any) {
      const msg = err?.response?.data?.mensagem || 'Erro de conexão.';
      setStepError(msg);
    }
  };

  // Landing institucional
  if (!mostrarFerramenta) {
    return (
      <LandingShell onBack={() => navigate(-1)}>
        <FluxogramaLanding onIniciar={() => { if (requireAuth()) setMostrarFerramenta(true); }} />
      </LandingShell>
    );
  }

  // Ferramenta de geração
  return (
    <Layout>
      <div className="fluxograma-page">
        <div className="fluxograma-header">
          <h1>Gerador de Fluxogramas</h1>
          <p>Descreva as etapas do processo ou importe um PDF de POP</p>
        </div>

        <div className="fluxograma-grid">
          {/* Coluna 1: Upload (opcional) */}
          <div className="fluxograma-card">
            <div className="card-header">
              <h2>1. Upload do POP (opcional)</h2>
              <p>Importe um PDF para pré-preencher dados, ou pule direto para a conversa</p>
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
                enabled
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
              defaultTitulo={popInfo?.atividade}
            />
          </div>
        </div>

        {/* Step List — visível após geração */}
        {conversaCompleta && steps.length > 0 && (
          <div className="fluxograma-card fluxograma-full-width">
            <div className="card-header">
              <h2>4. Etapas do Processo</h2>
              <p>Clique em uma etapa para editar ou use o botão para inserir novas</p>
            </div>
            <div className="card-body">
              <StepList
                steps={steps}
                activeStepId={activeStepId}
                onEdit={handleEditOpen}
                onInsertAfter={handleInsertAfter}
              />
            </div>
          </div>
        )}

        {/* Modal de edição/inserção */}
        {(editingStep || modalMode === 'insert') && insertAfterId !== null && modalMode === 'insert' && (
          <StepEditModal
            step={null}
            mode="insert"
            insertAfterLabel={editingStep?.label}
            onSave={handleModalSave}
            onRemove={handleRemoveStep}
            onClose={() => { setEditingStep(null); setInsertAfterId(null); setStepError(null); }}
          />
        )}
        {editingStep && modalMode === 'edit' && (
          <StepEditModal
            step={editingStep}
            mode="edit"
            onSave={handleModalSave}
            onRemove={handleRemoveStep}
            onClose={() => { setEditingStep(null); setStepError(null); }}
          />
        )}

        {/* Mensagem de erro inline */}
        {stepError && (
          <div style={{ color: '#c0392b', padding: '8px 16px', background: '#fdecea', borderRadius: 6, margin: '8px 0' }}>
            {stepError}
          </div>
        )}
      </div>
    </Layout>
  );
}
