import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './FerramentasApoioPage.css';
import { WizardAnaliseRiscos } from '../components/AnaliseRiscos';

interface Artefato {
  nome: string;
  descricao: string;
  url: string;
  dominio: number;
}

const CORES_DOMINIOS: { [key: number]: string } = {
  1: '#4a90e2',
  2: '#50c878',
  3: '#f5a623',
  4: '#9b59b6',
  5: '#e74c3c',
  6: '#ff6b6b',
  7: '#3498db'
};

const ARTEFATOS: Artefato[] = [
  // Domínio 1
  {
    nome: 'Canvas do Projeto',
    descricao: 'Para que usar: Ter visão geral do projeto em uma página. Como usar: Preencha propósito, beneficiários, entregas e valor público esperado.',
    url: '/dominio1/canvas',
    dominio: 1
  },
  {
    nome: 'Plano 5W2H',
    descricao: 'Para que usar: Planejar ações de forma estruturada. Como usar: Responda O quê? Quem? Quando? Onde? Por quê? Como? Quanto?',
    url: '/pop',
    dominio: 1
  },
  {
    nome: 'Cronograma Simplificado',
    descricao: 'Para que usar: Visualizar prazos e marcos principais. Como usar: Crie linha do tempo com início, fim e marcos intermediários.',
    url: '/dominio1/linha-tempo',
    dominio: 1
  },
  {
    nome: 'Checklist de Governança',
    descricao: 'Para que usar: Validar viabilidade institucional do projeto. Como usar: Marque itens de conformidade, alinhamento estratégico e aprovações.',
    url: '/dominio1/checklist',
    dominio: 1
  },

  // Domínio 2
  {
    nome: 'Canvas de Escopo e Valor',
    descricao: 'Para que usar: Delimitar o que será entregue. Como usar: Defina entregas, metas, resultados esperados e critérios de sucesso.',
    url: '/dominio2/canvas-escopo',
    dominio: 2
  },
  {
    nome: 'Matriz de Entregas e Responsáveis',
    descricao: 'Para que usar: Esclarecer papéis em cada entrega. Como usar: Marque quem é Responsável, Aprovador, Consultado e Informado (RACI).',
    url: '/dominio2/matriz-raci',
    dominio: 2
  },
  {
    nome: 'Painel de Indicadores de Valor Público',
    descricao: 'Para que usar: Monitorar impacto do projeto. Como usar: Defina indicadores de eficiência, impacto social e valor ao cidadão.',
    url: '/dominio2/indicadores',
    dominio: 2
  },
  {
    nome: 'Mapa de Exclusões e Restrições',
    descricao: 'Para que usar: Evitar desvios de escopo. Como usar: Liste o que NÃO faz parte do projeto e quais são os limites.',
    url: '/dominio2/exclusoes',
    dominio: 2
  },

  // Domínio 3
  {
    nome: 'Mapa de Papéis e Responsabilidades',
    descricao: 'Para que usar: Definir quem faz o quê. Como usar: Liste papéis, atribuições e poder de decisão de cada membro.',
    url: '/dominio3/mapa-papeis',
    dominio: 3
  },
  {
    nome: 'Organograma de Governança',
    descricao: 'Para que usar: Estruturar instâncias de decisão. Como usar: Desenhe hierarquia: comitês, gestores, equipe técnica.',
    url: '/dominio3/organograma',
    dominio: 3
  },
  {
    nome: 'Acordo de Trabalho da Equipe',
    descricao: 'Para que usar: Alinhar regras de colaboração. Como usar: Defina rituais, comunicação, horários e resolução de conflitos.',
    url: '/dominio3/acordo-trabalho',
    dominio: 3
  },
  {
    nome: 'Mapa de Competências do Projeto',
    descricao: 'Para que usar: Identificar gaps de habilidades. Como usar: Liste competências necessárias e avalie lacunas da equipe.',
    url: '/dominio3/mapa-competencias',
    dominio: 3
  },

  // Domínio 4
  {
    nome: 'Plano de Atividades e Recursos',
    descricao: 'Para que usar: Organizar tarefas e recursos. Como usar: Liste atividades, responsáveis, prazos e recursos necessários.',
    url: '/dominio4/plano-atividades',
    dominio: 4
  },
  {
    nome: 'Cronograma Operacional',
    descricao: 'Para que usar: Controlar prazos detalhados. Como usar: Crie Gantt ou timeline com dependências entre atividades.',
    url: '/dominio4/cronograma',
    dominio: 4
  },
  {
    nome: 'Mapa de Gargalos e Capacidades',
    descricao: 'Para que usar: Identificar restrições críticas. Como usar: Marque limitações de recursos, dependências e capacidades.',
    url: '/dominio4/mapa-gargalos',
    dominio: 4
  },
  {
    nome: 'Painel de Progresso Operacional',
    descricao: 'Para que usar: Acompanhar execução em tempo real. Como usar: Monitore atividades concluídas, em andamento e atrasadas.',
    url: '/dominio4/painel-progresso',
    dominio: 4
  },

  // Domínio 5
  {
    nome: 'Mapa de Partes Interessadas e Parceiros',
    descricao: 'Para que usar: Conhecer todos os atores envolvidos. Como usar: Liste stakeholders com poder, interesse e expectativas.',
    url: '/dominio5/mapa-stakeholders',
    dominio: 5
  },
  {
    nome: 'Matriz de Engajamento',
    descricao: 'Para que usar: Priorizar stakeholders. Como usar: Classifique por influência x interesse e defina estratégia.',
    url: '/dominio5/matriz-engajamento',
    dominio: 5
  },
  {
    nome: 'Plano de Comunicação',
    descricao: 'Para que usar: Garantir transparência. Como usar: Defina o quê comunicar, para quem, quando e por qual canal.',
    url: '/dominio5/plano-comunicacao',
    dominio: 5
  },
  {
    nome: 'Registro de Interações e Feedbacks',
    descricao: 'Para que usar: Documentar demandas e respostas. Como usar: Registre reuniões, manifestações e decisões tomadas.',
    url: '/dominio5/registro-feedbacks',
    dominio: 5
  },

  // Domínio 6
  {
    nome: 'Mapa de Contexto e Fatores Externos',
    descricao: 'Para que usar: Antecipar mudanças do ambiente. Como usar: Identifique fatores políticos, econômicos e legais que influenciam.',
    url: '/dominio6/mapa-contexto',
    dominio: 6
  },
  {
    nome: 'Matriz de Riscos e Controles',
    descricao: 'Para que usar: Avaliar riscos prioritários. Como usar: Classifique por probabilidade x impacto (ISO 31000).',
    url: '/dominio6/matriz-riscos',
    dominio: 6
  },
  {
    nome: 'Plano de Tratamento de Riscos',
    descricao: 'Para que usar: Mitigar riscos identificados. Como usar: Defina ações preventivas, responsáveis e prazos.',
    url: '/dominio6/plano-tratamento',
    dominio: 6
  },
  {
    nome: 'Registro de Ocorrências e Lições Aprendidas',
    descricao: 'Para que usar: Evitar erros recorrentes. Como usar: Documente incidentes, decisões críticas e aprendizados.',
    url: '/dominio6/registro-licoes',
    dominio: 6
  },

  // Domínio 7
  {
    nome: 'Painel de Resultados e Impacto',
    descricao: 'Para que usar: Medir desempenho do projeto. Como usar: Consolide indicadores quantitativos e qualitativos.',
    url: '/dominio7/painel-resultados',
    dominio: 7
  },
  {
    nome: 'Relatório de Lições Aprendidas',
    descricao: 'Para que usar: Gerar conhecimento institucional. Como usar: Registre sucessos, falhas e recomendações.',
    url: '/dominio7/relatorio-licoes',
    dominio: 7
  },
  {
    nome: 'Matriz de Sustentabilidade e Continuidade',
    descricao: 'Para que usar: Garantir continuidade dos ganhos. Como usar: Planeje manutenção e replicação de boas práticas.',
    url: '/dominio7/matriz-sustentabilidade',
    dominio: 7
  },
  {
    nome: 'Avaliação de Satisfação e Valor Público',
    descricao: 'Para que usar: Coletar percepção de valor. Como usar: Aplique pesquisas com beneficiários, parceiros e equipe.',
    url: '/dominio7/avaliacao-satisfacao',
    dominio: 7
  }
];

const FerramentasApoioPage: React.FC = () => {
  const navigate = useNavigate();
  const [mostrarWizardRiscos, setMostrarWizardRiscos] = useState(false);

  return (
    <div className="ferramentas-apoio-page">
      <div className="ferramentas-header-page">
        <button
          className="btn-voltar"
          onClick={() => navigate('/planejamento-estrategico')}
        >
          ← Voltar
        </button>
        <h1>🧰 Ferramentas de Apoio MGI</h1>
        <p className="subtitle">28 artefatos práticos para gerenciar seu projeto público</p>
      </div>

      <div className="ferramentas-lista-page">
        {ARTEFATOS.map((artefato, index) => (
          <div key={index} className="ferramenta-item">
            <span
              className="ferramenta-ponto"
              style={{ backgroundColor: CORES_DOMINIOS[artefato.dominio] }}
            />
            <div className="ferramenta-conteudo">
              <a
                href={artefato.url}
                className="ferramenta-nome"
              >
                {artefato.nome}
              </a>
              <p className="ferramenta-descricao">{artefato.descricao}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ========== BETA: Wizard Analise de Riscos (temporario) ========== */}
      <div style={{
        marginTop: '30px',
        padding: '20px',
        background: '#fef3c7',
        borderRadius: '8px',
        border: '2px dashed #f59e0b'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong style={{ color: '#92400e' }}>Analise de Riscos (BETA)</strong>
            <p style={{ margin: '5px 0 0', color: '#78350f', fontSize: '14px' }}>
              Wizard para identificar e analisar riscos de processos.
            </p>
          </div>
          <button
            onClick={() => setMostrarWizardRiscos(!mostrarWizardRiscos)}
            style={{
              padding: '8px 16px',
              background: mostrarWizardRiscos ? '#dc2626' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {mostrarWizardRiscos ? 'Fechar' : 'Abrir Wizard'}
          </button>
        </div>

        {mostrarWizardRiscos && (
          <div style={{ marginTop: '20px', background: 'white', borderRadius: '8px' }}>
            <WizardAnaliseRiscos tipoOrigem="POP" origemId="00000000-0000-0000-0000-000000000001" />
          </div>
        )}
      </div>
      {/* ========== FIM BETA ========== */}

    </div>
  );
};

export default FerramentasApoioPage;
