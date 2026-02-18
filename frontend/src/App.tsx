import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'

// Auth
import ProtectedRoute from './components/Auth/ProtectedRoute'
import AdminRoute from './components/Auth/AdminRoute'
import PublicRoute from './components/Auth/PublicRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import PendingAccessPage from './pages/PendingAccessPage'
import PasswordResetPage from './pages/PasswordResetPage'
import PasswordResetConfirmPage from './pages/PasswordResetConfirmPage'
import AdminUsersPage from './pages/AdminUsersPage'
import AdminDashboardPage from './pages/AdminDashboardPage'

// Pages
import Landing from './pages/Landing'
import Sobre from './pages/Sobre'
import Portal from './pages/Portal'
import MapeamentoProcessosPage from './pages/MapeamentoProcessosPage'
import AnaliseRiscosPage from './pages/AnaliseRiscos'
import FluxogramaPage from './pages/FluxogramaPage'
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
import CatalogoPOPPage from './pages/CatalogoPOPPage'
import CatalogoAreaPage from './pages/CatalogoAreaPage'
import CatalogoPOPDetailPage from './pages/CatalogoPOPDetailPage'
import FuncionalidadesPage from './pages/FuncionalidadesPage'
import LegalPage from './pages/LegalPage'
import PainelGestaoPage from './pages/PainelGestaoPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ================================================================
            ROTAS PUBLICAS — sem autenticacao
            ================================================================ */}
        <Route path="/" element={<Landing />} />
        <Route path="/sobre" element={<Sobre />} />
        <Route path="/funcionalidades" element={<FuncionalidadesPage />} />
        <Route path="/legal/:doc" element={<LegalPage />} />

        {/* Catalogo publico (somente leitura) */}
        <Route path="/catalogo" element={<CatalogoPOPPage />} />
        <Route path="/catalogo/:slug" element={<CatalogoAreaPage />} />
        <Route path="/catalogo/:slug/:codigo" element={<CatalogoPOPDetailPage />} />

        {/* ================================================================
            ROTAS DE AUTH — login, registro, verificacao, reset
            ================================================================ */}
        <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
        <Route path="/registrar" element={<PublicRoute><RegisterPage /></PublicRoute>} />
        <Route path="/verificar-email/:uid/:token" element={<VerifyEmailPage />} />
        <Route path="/acesso-pendente" element={<PendingAccessPage />} />
        <Route path="/recuperar-senha" element={<PasswordResetPage />} />
        <Route path="/nova-senha/:uid/:token" element={<PasswordResetConfirmPage />} />

        {/* ================================================================
            ROTAS ADMIN — painel administrativo + gestao de usuarios
            ================================================================ */}
        <Route path="/admin" element={<AdminRoute><AdminDashboardPage /></AdminRoute>} />
        <Route path="/admin/usuarios" element={<AdminRoute><AdminUsersPage /></AdminRoute>} />

        {/* ================================================================
            ROTAS PROTEGIDAS — exigem login + email verificado + acesso aprovado
            ================================================================ */}
        <Route path="/portal" element={<ProtectedRoute><Portal /></ProtectedRoute>} />

        {/* Landings publicas — gate interno protege a ferramenta */}
        <Route path="/pop" element={<MapeamentoProcessosPage />} />
        <Route path="/pop/chat" element={<MapeamentoProcessosPage startInChat />} />
        <Route path="/riscos" element={<AnaliseRiscosPage />} />
        <Route path="/fluxograma" element={<FluxogramaPage />} />
        <Route path="/plano" element={<ProtectedRoute><PlanoAcaoPage /></ProtectedRoute>} />
        <Route path="/painel" element={<PainelGestaoPage />} />

        {/* Planejamento Estrategico */}
        <Route path="/planejamento-estrategico" element={<ProtectedRoute><HelenaPEModerna /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/painel" element={<ProtectedRoute><HelenaPEModerna /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/modelos" element={<ProtectedRoute><HelenaPEModerna /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/diagnostico" element={<ProtectedRoute><DiagnosticoGuiado /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/modelos/tradicional" element={<ProtectedRoute><HelenaPEModerna /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/modelos/bsc" element={<ProtectedRoute><HelenaPEModerna /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/modelos/okr" element={<ProtectedRoute><MetodoIndividual /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/modelos/swot" element={<ProtectedRoute><HelenaPEModerna /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/modelos/cenarios" element={<ProtectedRoute><HelenaPEModerna /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/modelos/5w2h" element={<ProtectedRoute><HelenaPEModerna /></ProtectedRoute>} />
        <Route path="/planejamento-estrategico/modelos/hoshin" element={<ProtectedRoute><MetodoIndividual /></ProtectedRoute>} />

        {/* Dominios MGI */}
        <Route path="/dominio1" element={<ProtectedRoute><Dominio1 /></ProtectedRoute>} />
        <Route path="/dominio1/canvas" element={<ProtectedRoute><CanvasPage /></ProtectedRoute>} />
        <Route path="/dominio1/linha-tempo" element={<ProtectedRoute><LinhaTempoPage /></ProtectedRoute>} />
        <Route path="/dominio1/checklist" element={<ProtectedRoute><ChecklistPage /></ProtectedRoute>} />
        <Route path="/dominio2/canvas-escopo" element={<ProtectedRoute><CanvasEscopoPage /></ProtectedRoute>} />
        <Route path="/dominio2/matriz-raci" element={<ProtectedRoute><MatrizRACIPage /></ProtectedRoute>} />
        <Route path="/dominio2/indicadores" element={<ProtectedRoute><PainelIndicadoresPage /></ProtectedRoute>} />
        <Route path="/dominio2/exclusoes" element={<ProtectedRoute><MapaExclusoesPage /></ProtectedRoute>} />
        <Route path="/dominio3/mapa-papeis" element={<ProtectedRoute><MapaPapeisPage /></ProtectedRoute>} />
        <Route path="/dominio3/organograma" element={<ProtectedRoute><OrganogramaGovernancaPage /></ProtectedRoute>} />
        <Route path="/dominio3/acordo-trabalho" element={<ProtectedRoute><AcordoTrabalhoPage /></ProtectedRoute>} />
        <Route path="/dominio3/mapa-competencias" element={<ProtectedRoute><MapaCompetenciasPage /></ProtectedRoute>} />
        <Route path="/dominio4/plano-atividades" element={<ProtectedRoute><PlanoAtividadesPage /></ProtectedRoute>} />
        <Route path="/dominio4/cronograma" element={<ProtectedRoute><CronogramaPage /></ProtectedRoute>} />
        <Route path="/dominio4/mapa-gargalos" element={<ProtectedRoute><MapaGargalosPage /></ProtectedRoute>} />
        <Route path="/dominio4/painel-progresso" element={<ProtectedRoute><PainelProgressoPage /></ProtectedRoute>} />
        <Route path="/dominio5/mapa-stakeholders" element={<ProtectedRoute><MapaStakeholdersPage /></ProtectedRoute>} />
        <Route path="/dominio5/matriz-engajamento" element={<ProtectedRoute><MatrizEngajamentoPage /></ProtectedRoute>} />
        <Route path="/dominio5/plano-comunicacao" element={<ProtectedRoute><PlanoComunicacaoPage /></ProtectedRoute>} />
        <Route path="/dominio5/registro-feedbacks" element={<ProtectedRoute><RegistroFeedbacksPage /></ProtectedRoute>} />
        <Route path="/dominio6/mapa-contexto" element={<ProtectedRoute><MapaContextoPage /></ProtectedRoute>} />
        <Route path="/dominio6/matriz-riscos" element={<ProtectedRoute><MatrizRiscosControlesPage /></ProtectedRoute>} />
        <Route path="/dominio6/plano-tratamento" element={<ProtectedRoute><PlanoTratamentoRiscosPage /></ProtectedRoute>} />
        <Route path="/dominio6/registro-licoes" element={<ProtectedRoute><RegistroLicoesAprendidasPage /></ProtectedRoute>} />
        <Route path="/dominio7/painel-resultados" element={<ProtectedRoute><PainelResultadosImpactoPage /></ProtectedRoute>} />
        <Route path="/dominio7/relatorio-licoes" element={<ProtectedRoute><RelatorioLicoesAprendidasPage /></ProtectedRoute>} />
        <Route path="/dominio7/matriz-sustentabilidade" element={<ProtectedRoute><MatrizSustentabilidadePage /></ProtectedRoute>} />
        <Route path="/dominio7/avaliacao-satisfacao" element={<ProtectedRoute><AvaliacaoSatisfacaoPage /></ProtectedRoute>} />

        {/* Ferramentas e Metodos */}
        <Route path="/ferramentas-apoio" element={<ProtectedRoute><FerramentasApoioPage /></ProtectedRoute>} />
        <Route path="/metodos" element={<ProtectedRoute><MetodosPage /></ProtectedRoute>} />
        <Route path="/metodos/:metodoId" element={<ProtectedRoute><MetodoIndividual /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
