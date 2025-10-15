import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'
import Landing from './pages/Landing'
import Sobre from './pages/Sobre'
import Portal from './pages/Portal'
import ChatContainer from './components/Helena/ChatContainer'
import FormularioPOP from './components/Helena/FormularioPOP'
import AnaliseRiscosPage from './pages/AnaliseRiscos'
import FluxogramaPage from './pages/FluxogramaPage'

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
      </Routes>
    </BrowserRouter>
  )
}

export default App