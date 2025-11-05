import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'
import Landing from './pages/Landing'
import Sobre from './pages/Sobre'
import Portal from './pages/Portal'
import ChatContainer from './components/Helena/ChatContainer'
import FormularioPOP from './components/Helena/FormularioPOP'
import AnaliseRiscosPage from './pages/AnaliseRiscos'
import FluxogramaPage from './pages/FluxogramaPage'
import ChatV2Demo from './components/Helena/ChatV2Demo'
import PlanoAcaoPage from './pages/PlanoAcaoPage'
import HelenaPEModerna from './pages/HelenaPEModerna'
import Dominio1 from './pages/Dominio1'
import CanvasPage from './pages/CanvasPage'
import LinhaTempoPage from './pages/LinhaTempoPage'
import ChecklistPage from './pages/ChecklistPage'
import DiagnosticoGuiado from './pages/DiagnosticoGuiado'
import CanvasEscopoPage from './pages/CanvasEscopoPage'
import MatrizRACIPage from './pages/MatrizRACIPage'
import PainelIndicadoresPage from './pages/PainelIndicadoresPage'
import MapaExclusoesPage from './pages/MapaExclusoesPage'
import MapaPapeisPage from './pages/MapaPapeisPage'
import OrganogramaGovernancaPage from './pages/OrganogramaGovernancaPage'
import AcordoTrabalhoPage from './pages/AcordoTrabalhoPage'
import MapaCompetenciasPage from './pages/MapaCompetenciasPage'
import PlanoAtividadesPage from './pages/PlanoAtividadesPage'
import CronogramaPage from './pages/CronogramaPage'
import MapaGargalosPage from './pages/MapaGargalosPage'
import PainelProgressoPage from './pages/PainelProgressoPage'
import MapaStakeholdersPage from './pages/MapaStakeholdersPage'
import MatrizEngajamentoPage from './pages/MatrizEngajamentoPage'
import PlanoComunicacaoPage from './pages/PlanoComunicacaoPage'
import RegistroFeedbacksPage from './pages/RegistroFeedbacksPage'
import MapaContextoPage from './pages/MapaContextoPage'
import MatrizRiscosControlesPage from './pages/MatrizRiscosControlesPage'
import PlanoTratamentoRiscosPage from './pages/PlanoTratamentoRiscosPage'
import RegistroLicoesAprendidasPage from './pages/RegistroLicoesAprendidasPage'
import PainelResultadosImpactoPage from './pages/PainelResultadosImpactoPage'
import RelatorioLicoesAprendidasPage from './pages/RelatorioLicoesAprendidasPage'
import MatrizSustentabilidadePage from './pages/MatrizSustentabilidadePage'
import AvaliacaoSatisfacaoPage from './pages/AvaliacaoSatisfacaoPage'
import FerramentasApoioPage from './pages/FerramentasApoioPage'
import MetodosPage from './pages/MetodosPage'
import MetodoIndividual from './pages/MetodoIndividual'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rota Principal: Landing Page */}
        <Route path="/" element={<Landing />} />

        {/* Rota: Sobre MapaGov */}
        <Route path="/sobre" element={<Sobre />} />

        {/* Rota: Portal de Produtos */}
        <Route path="/portal" element={<Portal />} />

        {/* Rota: Chat POP */}
        <Route
          path="/chat"
          element={
            <div className="app-container">
              <div className="chat-section">
                <ChatContainer />
              </div>
              <FormularioPOP />
            </div>
          }
        />

        {/* Rota: Análise de Riscos */}
        <Route path="/riscos" element={<AnaliseRiscosPage />} />

        {/* Rota: Gerador de Fluxogramas */}
        <Route path="/fluxograma" element={<FluxogramaPage />} />

        {/* 🚀 FASE 1 - Demo da Nova API */}
        <Route path="/chat-v2" element={<ChatV2Demo />} />

        {/* P6 - Plano de Ação */}
        <Route path="/plano" element={<PlanoAcaoPage />} />

        {/* Helena Planejamento Estratégico - Hierarquia organizada */}
        <Route path="/planejamento-estrategico" element={<HelenaPEModerna />} />
        <Route path="/planejamento-estrategico/modelos" element={<HelenaPEModerna />} />
        <Route path="/planejamento-estrategico/diagnostico" element={<DiagnosticoGuiado />} />

        {/* Workspaces dos Modelos (hierarquia /planejamento-estrategico/modelos/...) */}
        <Route path="/planejamento-estrategico/modelos/tradicional" element={<HelenaPEModerna />} />
        <Route path="/planejamento-estrategico/modelos/bsc" element={<HelenaPEModerna />} />
        <Route path="/planejamento-estrategico/modelos/okr" element={<MetodoIndividual />} />
        <Route path="/planejamento-estrategico/modelos/swot" element={<HelenaPEModerna />} />
        <Route path="/planejamento-estrategico/modelos/cenarios" element={<HelenaPEModerna />} />
        <Route path="/planejamento-estrategico/modelos/5w2h" element={<HelenaPEModerna />} />
        <Route path="/planejamento-estrategico/modelos/hoshin" element={<MetodoIndividual />} />

        {/* Domínios MGI */}
        <Route path="/dominio1" element={<Dominio1 />} />

        {/* Artefatos Domínio 1 */}
        <Route path="/dominio1/canvas" element={<CanvasPage />} />
        <Route path="/dominio1/linha-tempo" element={<LinhaTempoPage />} />
        <Route path="/dominio1/checklist" element={<ChecklistPage />} />

        {/* Artefatos Domínio 2 */}
        <Route path="/dominio2/canvas-escopo" element={<CanvasEscopoPage />} />
        <Route path="/dominio2/matriz-raci" element={<MatrizRACIPage />} />
        <Route path="/dominio2/indicadores" element={<PainelIndicadoresPage />} />
        <Route path="/dominio2/exclusoes" element={<MapaExclusoesPage />} />

        {/* Artefatos Domínio 3 */}
        <Route path="/dominio3/mapa-papeis" element={<MapaPapeisPage />} />
        <Route path="/dominio3/organograma" element={<OrganogramaGovernancaPage />} />
        <Route path="/dominio3/acordo-trabalho" element={<AcordoTrabalhoPage />} />
        <Route path="/dominio3/mapa-competencias" element={<MapaCompetenciasPage />} />

        {/* Artefatos Domínio 4 */}
        <Route path="/dominio4/plano-atividades" element={<PlanoAtividadesPage />} />
        <Route path="/dominio4/cronograma" element={<CronogramaPage />} />
        <Route path="/dominio4/mapa-gargalos" element={<MapaGargalosPage />} />
        <Route path="/dominio4/painel-progresso" element={<PainelProgressoPage />} />

        {/* Artefatos Domínio 5 */}
        <Route path="/dominio5/mapa-stakeholders" element={<MapaStakeholdersPage />} />
        <Route path="/dominio5/matriz-engajamento" element={<MatrizEngajamentoPage />} />
        <Route path="/dominio5/plano-comunicacao" element={<PlanoComunicacaoPage />} />
        <Route path="/dominio5/registro-feedbacks" element={<RegistroFeedbacksPage />} />

        {/* Artefatos Domínio 6 */}
        <Route path="/dominio6/mapa-contexto" element={<MapaContextoPage />} />
        <Route path="/dominio6/matriz-riscos" element={<MatrizRiscosControlesPage />} />
        <Route path="/dominio6/plano-tratamento" element={<PlanoTratamentoRiscosPage />} />
        <Route path="/dominio6/registro-licoes" element={<RegistroLicoesAprendidasPage />} />

        {/* Artefatos Domínio 7 */}
        <Route path="/dominio7/painel-resultados" element={<PainelResultadosImpactoPage />} />
        <Route path="/dominio7/relatorio-licoes" element={<RelatorioLicoesAprendidasPage />} />
        <Route path="/dominio7/matriz-sustentabilidade" element={<MatrizSustentabilidadePage />} />
        <Route path="/dominio7/avaliacao-satisfacao" element={<AvaliacaoSatisfacaoPage />} />

        {/* Página Ferramentas de Apoio */}
        <Route path="/ferramentas-apoio" element={<FerramentasApoioPage />} />

        {/* Página Métodos de Gestão */}
        <Route path="/metodos" element={<MetodosPage />} />
        <Route path="/metodos/:metodoId" element={<MetodoIndividual />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App