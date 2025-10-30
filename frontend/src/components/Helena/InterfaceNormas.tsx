import React, { useState, useMemo } from "react";
import { ChevronDown, ChevronRight, Search } from "lucide-react";
import ReactMarkdown from 'react-markdown';

interface Norma {
  nome_curto: string;
  nome_completo: string;
  artigos: string;
  confianca?: number;
  grupo?: string;
  label?: string;
}

interface InterfaceNormasProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceNormas: React.FC<InterfaceNormasProps> = ({ dados, onConfirm }) => {
  const [normasSelecionadas, setNormasSelecionadas] = useState<string[]>([]);
  const [categoriaAberta, setCategoriaAberta] = useState<string | null>(null);
  const [mostrarTodas, setMostrarTodas] = useState(false);
  const [mostrarNormasManuais, setMostrarNormasManuais] = useState(false);
  const [normasManuais, setNormasManuais] = useState<string[]>(['']);
  const [termoBusca, setTermoBusca] = useState<string>('');


  // Extrair sugestões do backend (top 3)
  const sugestoes = useMemo(() => {
    const sugestoesDados = (dados as { sugestoes?: Norma[] })?.sugestoes;
    if (sugestoesDados && Array.isArray(sugestoesDados)) {
      return sugestoesDados;
    }
    return [];
  }, [dados]);

  // Extrair grupos de normas do backend (DECIPEX v2.2)
  const categorias = useMemo(() => {
    const gruposDados = (dados as { grupos?: Record<string, { label: string; itens: Norma[] }> })?.grupos;

    // Se não vier do backend, retornar vazio (não usar mais fallback hardcoded)
    if (!gruposDados || typeof gruposDados !== 'object') {
      return {};
    }

    // Converter estrutura do backend para formato do frontend
    const categoriasFormatadas: Record<string, Norma[]> = {};

    Object.entries(gruposDados).forEach(([grupoKey, grupoData]) => {
      const label = grupoData.label || grupoKey;
      categoriasFormatadas[label] = grupoData.itens || [];
    });

    return categoriasFormatadas;
  }, [dados]);

  const toggleNorma = (nomeCompleto: string) => {
    setNormasSelecionadas(prev =>
      prev.includes(nomeCompleto)
        ? prev.filter(n => n !== nomeCompleto)
        : [...prev, nomeCompleto]
    );
  };

  const toggleCategoria = (categoria: string) => {
    setCategoriaAberta(prev => (prev === categoria ? null : categoria));
  };

  const selecionarTodasSugestoes = () => {
    const nomesSugestoes = sugestoes.map(s => s.nome_completo);
    setNormasSelecionadas(nomesSugestoes);
  };

  const limparSelecao = () => {
    setNormasSelecionadas([]);
  };

  const adicionarCampoNormaManual = () => {
    setNormasManuais([...normasManuais, '']);
  };

  const removerCampoNormaManual = (index: number) => {
    if (normasManuais.length > 1) {
      setNormasManuais(normasManuais.filter((_, i) => i !== index));
    }
  };

  const atualizarNormaManual = (index: number, valor: string) => {
    const novasNormas = [...normasManuais];
    novasNormas[index] = valor;
    setNormasManuais(novasNormas);
  };

  const abrirIALegis = () => {
    window.open('https://legis.sigepe.gov.br/legis/chat-legis', '_blank');
  };

  // Filtrar categorias por termo de busca
  const categoriasFiltradas = useMemo(() => {
    if (!termoBusca.trim()) {
      return categorias;
    }

    const termo = termoBusca.toLowerCase();
    const resultado: Record<string, Norma[]> = {};

    Object.entries(categorias).forEach(([categoria, normas]) => {
      const normasFiltradas = normas.filter(norma =>
        norma.nome_curto.toLowerCase().includes(termo) ||
        norma.nome_completo.toLowerCase().includes(termo) ||
        norma.artigos.toLowerCase().includes(termo)
      );

      if (normasFiltradas.length > 0) {
        resultado[categoria] = normasFiltradas;
      }
    });

    return resultado;
  }, [categorias, termoBusca]);

  const handleConfirm = () => {
    // Combinar normas selecionadas + normas manuais (filtrar vazias)
    const normsManuaisPreenchidas = normasManuais.filter(n => n.trim().length > 0);
    const todasNormas = [...normasSelecionadas, ...normsManuaisPreenchidas];

    const resposta = todasNormas.length > 0
      ? todasNormas.join(" | ")
      : "nenhuma";
    onConfirm(resposta);
  };

  // Extrair texto de introdução (se houver)
  const textoIntroducao = (dados as { texto_introducao?: string })?.texto_introducao;

  return (
    <div className="interface-container fade-in">
      {/* Texto de Introdução (vem do backend) */}
      {textoIntroducao && (
        <div className="interface-intro" style={{
          marginBottom: '20px',
          padding: '16px',
          background: '#f8f9fa',
          borderRadius: '8px',
          borderLeft: '4px solid #1351B4'
        }}>
          <ReactMarkdown>{textoIntroducao}</ReactMarkdown>
        </div>
      )}

      {/* Cabeçalho Unificado */}
      <div className="interface-title">📚 Normas e Dispositivos Legais</div>
      <div className="interface-subtitle">
        Essas são as normas que encontrei para sua atividade. Você pode aceitar as sugestões, explorar a biblioteca completa ou buscar/adicionar manualmente.
      </div>

      {/* Contador de Seleção - Chips Removíveis */}
      {normasSelecionadas.length > 0 && (
        <div className="chips-container">
          <div className="chips-header">
            <span className="chips-count">{normasSelecionadas.length} norma(s) selecionada(s) ✅</span>
            <button className="btn-limpar-chips" onClick={limparSelecao} type="button">
              Limpar todas
            </button>
          </div>
          <div className="chips-list">
            {normasSelecionadas.map((normaCompleta, idx) => (
              <div key={idx} className="chip">
                <span className="chip-text">{normaCompleta}</span>
                <button
                  className="chip-remove"
                  onClick={() => toggleNorma(normaCompleta)}
                  type="button"
                  aria-label="Remover norma"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Layout Vertical Progressivo */}
      <div className="vertical-progressive-layout">

        {/* 1️⃣ SEÇÃO: SUGESTÕES AUTOMÁTICAS (HELENA) */}
        <div className="section-card section-sugestoes">
          <div className="section-header">
            <h3>💡 Minhas Sugestões</h3>
            <p className="section-desc">Essas são as normas que encontrei para sua atividade</p>
            {sugestoes.length > 0 && (
              <button
                className="btn-inline-action"
                onClick={selecionarTodasSugestoes}
                type="button"
              >
                Selecionar todas
              </button>
            )}
          </div>

          {sugestoes.length > 0 ? (
            <div className="normas-list">
              {sugestoes.map((norma, idx) => (
                <div
                  key={idx}
                  className={`norma-card ${normasSelecionadas.includes(norma.nome_completo) ? 'selected' : ''}`}
                  onClick={() => toggleNorma(norma.nome_completo)}
                >
                  <input
                    type="checkbox"
                    readOnly
                    checked={normasSelecionadas.includes(norma.nome_completo)}
                  />
                  <div className="norma-info">
                    {norma.label && (
                      <div className="norma-grupo-label">{norma.label}</div>
                    )}
                    <strong>{norma.nome_curto}</strong>
                    <p>{norma.nome_completo}</p>
                    <small>Artigos: {norma.artigos}</small>
                    {norma.confianca && (
                      <span className="confianca">Relevância: {norma.confianca}%</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Nenhuma sugestão disponível para este contexto.</p>
            </div>
          )}
        </div>

        {/* 2️⃣ SEÇÃO: EXPLORAR BIBLIOTECA COMPLETA */}
        <div className="section-card section-biblioteca">
          <div className="section-header">
            <h3>📚 Explorar Biblioteca Completa</h3>
            <p className="section-desc">Quer ver todas as normas da nossa biblioteca? Busque por tema ou nome.</p>
          </div>

          {/* Campo de Busca Instantânea */}
          <div className="search-container">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="🔎 Buscar por nome, número ou artigo da norma..."
              value={termoBusca}
              onChange={(e) => setTermoBusca(e.target.value)}
            />
            {termoBusca && (
              <button
                className="clear-search"
                onClick={() => setTermoBusca('')}
                type="button"
              >
                ✕
              </button>
            )}
          </div>

          {/* Acordeão de Categorias */}
          {Object.keys(categoriasFiltradas).length > 0 ? (
            <div className="categorias-acordeao">
              {Object.entries(categoriasFiltradas).map(([categoria, normas]) => (
                <div key={categoria} className="categoria-item">
                  <div
                    className="categoria-header"
                    onClick={() => toggleCategoria(categoria)}
                  >
                    {categoriaAberta === categoria ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                    <span>{categoria}</span>
                    <span className="categoria-count">({normas.length})</span>
                  </div>

                  {categoriaAberta === categoria && (
                    <div className="normas-list-categoria">
                      {normas.map((norma, idx) => (
                        <div
                          key={idx}
                          className={`norma-card-small ${normasSelecionadas.includes(norma.nome_completo) ? 'selected' : ''}`}
                          onClick={() => toggleNorma(norma.nome_completo)}
                        >
                          <input
                            type="checkbox"
                            readOnly
                            checked={normasSelecionadas.includes(norma.nome_completo)}
                          />
                          <div className="norma-info-small">
                            <strong>{norma.nome_curto}</strong>
                            <small>{norma.artigos}</small>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Nenhuma norma encontrada para "{termoBusca}"</p>
            </div>
          )}
        </div>

        {/* 3️⃣ SEÇÃO: BUSCAR / ADICIONAR - Ações Finais */}
        <div className="section-card section-actions">
          <div className="section-header">
            <h3>🔍 Não encontrou?</h3>
            <p className="section-desc">Você pode tentar a busca inteligente ou adicionar manualmente.</p>
          </div>

          <div className="actions-row">
            {/* Botão IA Legis */}
            <div className="action-group">
              <button
                className="btn-ia-legis"
                onClick={abrirIALegis}
                type="button"
                title="A IA do Legis vai procurar outras normas relacionadas ao seu processo"
              >
                🔍 Consultar IA do Sigepe Legis
              </button>
              <small className="action-hint">A IA do Legis procura outras normas relacionadas</small>
            </div>

            {/* Botão Adicionar Manualmente */}
            <div className="action-group">
              {!mostrarNormasManuais ? (
                <button
                  className="btn-adicionar-manual"
                  onClick={() => setMostrarNormasManuais(true)}
                  type="button"
                >
                  ➕ Adicionar norma manualmente
                </button>
              ) : (
                <button
                  className="btn-cancelar-manual"
                  onClick={() => setMostrarNormasManuais(false)}
                  type="button"
                >
                  Cancelar
                </button>
              )}
            </div>
          </div>

          {/* Seção de Normas Manuais (inline) */}
          {mostrarNormasManuais && (
            <div className="normas-manuais-inline">
              {normasManuais.map((norma, index) => (
                <div key={index} className="norma-manual-row">
                  <input
                    type="text"
                    className="norma-manual-input"
                    placeholder="Ex: Art. 34 da IN SGP nº 97/2022"
                    value={norma}
                    onChange={(e) => atualizarNormaManual(index, e.target.value)}
                    maxLength={300}
                  />
                  <button
                    className="btn-adicionar-manual-confirmar"
                    onClick={adicionarCampoNormaManual}
                    type="button"
                    title="Adicionar"
                  >
                    Adicionar
                  </button>
                  {normasManuais.length > 1 && (
                    <button
                      className="btn-remover-norma"
                      onClick={() => removerCampoNormaManual(index)}
                      type="button"
                      title="Remover"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Rodapé - Ações de Confirmação */}
      <div className="footer-actions">
        <button className="btn-interface btn-secondary" onClick={() => onConfirm('nao sei')}>
          Não Sei
        </button>
        <button
          className="btn-interface btn-primary"
          onClick={handleConfirm}
          disabled={normasSelecionadas.length === 0}
        >
          Confirmar {normasSelecionadas.length > 0 && `(${normasSelecionadas.length})`}
        </button>
      </div>

      <style>{`
        /* ========== CABEÇALHO ========== */
        .interface-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1351B4;
          margin-bottom: 0.5rem;
          text-align: center;
        }

        .interface-subtitle {
          font-size: 0.9rem;
          color: #6c757d;
          text-align: center;
          margin-bottom: 1.5rem;
          line-height: 1.5;
        }

        /* ========== CHIPS CONTAINER (Normas Selecionadas) ========== */
        .chips-container {
          margin-bottom: 1.5rem;
          padding: 1rem;
          background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
          border: 2px solid #66bb6a;
          border-radius: 12px;
          animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .chips-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.75rem;
        }

        .chips-count {
          font-weight: 600;
          color: #2e7d32;
          font-size: 0.95rem;
        }

        .btn-limpar-chips {
          padding: 0.4rem 0.9rem;
          background: white;
          color: #d32f2f;
          border: 1px solid #d32f2f;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-limpar-chips:hover {
          background: #d32f2f;
          color: white;
        }

        .chips-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .chip {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.4rem 0.75rem;
          background: white;
          border: 1px solid #66bb6a;
          border-radius: 20px;
          font-size: 0.85rem;
          max-width: 100%;
          transition: all 0.2s;
        }

        .chip:hover {
          box-shadow: 0 2px 8px rgba(102, 187, 106, 0.3);
        }

        .chip-text {
          flex: 1;
          color: #2e7d32;
          font-weight: 500;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .chip-remove {
          background: transparent;
          border: none;
          color: #d32f2f;
          font-size: 1rem;
          font-weight: bold;
          cursor: pointer;
          padding: 0;
          width: 18px;
          height: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          transition: all 0.2s;
        }

        .chip-remove:hover {
          background: #d32f2f;
          color: white;
        }

        /* ========== LAYOUT VERTICAL PROGRESSIVO ========== */
        .vertical-progressive-layout {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          margin-bottom: 1.5rem;
        }

        /* ========== SEÇÃO CARD (Comum) ========== */
        .section-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          border: 2px solid #e0e6ed;
          transition: all 0.3s;
        }

        .section-card:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .section-sugestoes {
          border-left: 4px solid #1351B4;
        }

        .section-biblioteca {
          border-left: 4px solid #6c757d;
        }

        .section-actions {
          border-left: 4px solid #28a745;
          background: #f8f9fa;
        }

        .section-header {
          position: relative;
          margin-bottom: 1.25rem;
        }

        .section-header h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.1rem;
          color: #1351B4;
          font-weight: 600;
        }

        .section-desc {
          margin: 0 0 0.75rem 0;
          font-size: 0.85rem;
          color: #6c757d;
          line-height: 1.5;
        }

        .btn-inline-action {
          position: absolute;
          top: 0;
          right: 0;
          padding: 0.4rem 0.9rem;
          background: #1351B4;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 0.8rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-inline-action:hover {
          background: #0d3a85;
          transform: translateY(-1px);
        }

        /* ========== EMPTY STATE ========== */
        .empty-state {
          text-align: center;
          padding: 2rem;
          color: #6c757d;
          font-size: 0.9rem;
        }

        /* ========== BUSCA INSTANTÂNEA ========== */
        .search-container {
          position: relative;
          margin-bottom: 1rem;
        }

        .search-icon {
          position: absolute;
          left: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: #6c757d;
        }

        .search-input {
          width: 100%;
          padding: 0.75rem 2.5rem 0.75rem 2.5rem;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          font-size: 0.9rem;
          transition: all 0.2s;
        }

        .search-input:focus {
          outline: none;
          border-color: #1351B4;
          box-shadow: 0 0 0 3px rgba(19, 81, 180, 0.1);
        }

        .clear-search {
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 0.9rem;
          transition: all 0.2s;
        }

        .clear-search:hover {
          background: #c82333;
        }

        /* ========== AÇÕES ROW (IA Legis + Adicionar Manual) ========== */
        .actions-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-top: 1rem;
        }

        @media (max-width: 768px) {
          .actions-row {
            grid-template-columns: 1fr;
          }
        }

        .action-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .action-hint {
          color: #6c757d;
          font-size: 0.75rem;
          text-align: center;
        }

        .btn-ia-legis {
          width: 100%;
          padding: 0.9rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 0.9rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .btn-ia-legis:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-adicionar-manual {
          width: 100%;
          padding: 0.9rem;
          background: white;
          color: #28a745;
          border: 2px dashed #28a745;
          border-radius: 8px;
          font-size: 0.9rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-adicionar-manual:hover {
          background: #28a745;
          color: white;
          border-style: solid;
        }

        .btn-cancelar-manual {
          width: 100%;
          padding: 0.9rem;
          background: #6c757d;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 0.9rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-cancelar-manual:hover {
          background: #5a6268;
        }

        /* ========== NORMAS MANUAIS INLINE ========== */
        .normas-manuais-inline {
          margin-top: 1rem;
          padding: 1rem;
          background: white;
          border: 2px dashed #28a745;
          border-radius: 8px;
          animation: fadeIn 0.3s ease-in;
        }

        /* ========== FOOTER ACTIONS ========== */
        .footer-actions {
          margin-top: 2rem;
          padding-top: 1.5rem;
          border-top: 3px solid #1351B4;
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        /* ========== CARDS DE NORMAS ========== */
        .normas-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .norma-card {
          display: flex;
          gap: 1rem;
          padding: 1rem;
          background: white;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .norma-card:hover {
          border-color: #1351B4;
          box-shadow: 0 2px 8px rgba(19, 81, 180, 0.15);
          transform: translateX(4px);
        }

        .norma-card.selected {
          border-color: #28a745;
          background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
          animation: selectedPulse 0.3s ease-in;
        }

        @keyframes selectedPulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.02); }
          100% { transform: scale(1); }
        }

        .norma-card input[type="checkbox"] {
          margin-top: 0.25rem;
          cursor: pointer;
        }

        .norma-info {
          flex: 1;
        }

        .norma-grupo-label {
          display: inline-block;
          margin-bottom: 0.5rem;
          padding: 0.25rem 0.75rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          letter-spacing: 0.3px;
        }

        .norma-info strong {
          color: #1351B4;
          font-size: 1rem;
        }

        .norma-info p {
          margin: 0.25rem 0;
          font-size: 0.9rem;
          color: #495057;
        }

        .norma-info small {
          color: #6c757d;
          font-size: 0.85rem;
        }

        .confianca {
          display: inline-block;
          margin-left: 1rem;
          padding: 0.25rem 0.5rem;
          background: #28a745;
          color: white;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: bold;
        }

        .visualizar-mais-section {
          margin: 1.5rem 0;
          text-align: center;
        }

        .btn-visualizar-mais {
          padding: 0.75rem 1.5rem;
          background: #6c757d;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-visualizar-mais:hover {
          background: #5a6268;
        }

        .nao-encontrei-section {
          margin: 1.5rem 0;
          text-align: center;
        }

        .btn-nao-encontrei {
          padding: 1rem 2rem;
          background: #ffc107;
          color: #856404;
          border: 2px solid #ffc107;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
          box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
        }

        .btn-nao-encontrei:hover {
          background: #ffca2c;
          border-color: #ffca2c;
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(255, 193, 7, 0.3);
        }

        .categorias-acordeao {
          margin-top: 1rem;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          overflow: hidden;
        }

        .categoria-item {
          border-bottom: 1px solid #dee2e6;
        }

        .categoria-item:last-child {
          border-bottom: none;
        }

        .categoria-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: #f8f9fa;
          cursor: pointer;
          transition: all 0.2s;
        }

        .categoria-header:hover {
          background: #e9ecef;
        }

        .categoria-header span:first-of-type {
          flex: 1;
          font-weight: 600;
          color: #495057;
        }

        .categoria-count {
          font-weight: 400;
          color: #6c757d;
          font-size: 0.85rem;
        }

        .normas-list-categoria {
          padding: 1rem;
          background: white;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .norma-card-small {
          display: flex;
          gap: 0.75rem;
          padding: 0.75rem;
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .norma-card-small:hover {
          border-color: #1351B4;
          background: #f0f4ff;
          transform: translateX(4px);
        }

        .norma-card-small.selected {
          border-color: #28a745;
          background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
          animation: selectedPulse 0.3s ease-in;
        }

        .norma-info-small {
          flex: 1;
        }

        .norma-info-small strong {
          color: #1351B4;
          font-size: 0.9rem;
        }

        .norma-info-small small {
          display: block;
          color: #6c757d;
          font-size: 0.8rem;
          margin-top: 0.25rem;
        }

        .contador-e-limpar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 1rem;
          margin: 1rem 0;
          padding: 0.75rem;
          background: #f8f9fa;
          border-radius: 6px;
        }

        .contador-normas {
          font-weight: 500;
          color: #495057;
        }

        .btn-limpar-selecao {
          padding: 0.5rem 1rem;
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
          white-space: nowrap;
        }

        .btn-limpar-selecao:hover {
          background: #c82333;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .btn-interface {
          flex: 1;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
        }

        .normas-manuais-section {
          margin-top: 1rem;
          padding: 1rem;
          background: #f8f9fa;
          border: 2px dashed #6c757d;
          border-radius: 8px;
        }

        .normas-manuais-header h4 {
          margin: 0 0 1rem 0;
          color: #495057;
          font-size: 0.95rem;
        }

        .norma-manual-row {
          display: flex;
          gap: 0.75rem;
          margin-bottom: 0.75rem;
          align-items: center;
        }

        .norma-manual-input {
          flex: 1;
          padding: 0.75rem;
          border: 2px solid #dee2e6;
          border-radius: 6px;
          font-size: 0.95rem;
          transition: all 0.2s;
        }

        .norma-manual-input:focus {
          outline: none;
          border-color: #28a745;
          box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
        }

        .norma-manual-input::placeholder {
          color: #adb5bd;
        }

        .btn-adicionar-manual-confirmar {
          padding: 0.75rem 1.25rem;
          background: #28a745;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 0.9rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
        }

        .btn-adicionar-manual-confirmar:hover {
          background: #218838;
          transform: translateY(-1px);
        }

        .btn-remover-norma {
          min-width: 40px;
          height: 40px;
          border: 2px solid #dc3545;
          background: white;
          color: #dc3545;
          border-radius: 6px;
          cursor: pointer;
          font-size: 1.2rem;
          font-weight: bold;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .btn-remover-norma:hover {
          background: #dc3545;
          color: white;
        }
      `}</style>
    </div>
  );
};

export default InterfaceNormas;