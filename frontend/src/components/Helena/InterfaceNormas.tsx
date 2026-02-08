import React, { useState, useMemo } from "react";
import { ChevronDown, ChevronRight, Search } from "lucide-react";
import ReactMarkdown from 'react-markdown';

interface Norma {
  nome_curto: string;
  nome_completo: string;
  artigos: string;
}

interface InterfaceNormasProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceNormas: React.FC<InterfaceNormasProps> = ({ dados, onConfirm }) => {
  const [normasSelecionadas, setNormasSelecionadas] = useState<string[]>([]);
  const [categoriaAberta, setCategoriaAberta] = useState<string | null>(null);
  const [mostrarNormasManuais, setMostrarNormasManuais] = useState(false);
  const [normasManuais, setNormasManuais] = useState<string[]>([]);
  const [normaManualInput, setNormaManualInput] = useState<string>('');
  const [termoBusca, setTermoBusca] = useState<string>('');

  // Extrair grupos de normas do backend
  const categorias = useMemo(() => {
    const gruposDados = (dados as { grupos?: Record<string, { label: string; itens: Norma[] }> })?.grupos;

    if (!gruposDados || typeof gruposDados !== 'object') {
      return {};
    }

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

  const limparSelecao = () => {
    setNormasSelecionadas([]);
  };

  const adicionarNormaManual = () => {
    const norma = normaManualInput.trim();
    if (norma && !normasManuais.includes(norma) && !normasSelecionadas.includes(norma)) {
      setNormasManuais([...normasManuais, norma]);
      setNormaManualInput('');
    }
  };

  const removerNormaManual = (norma: string) => {
    setNormasManuais(normasManuais.filter(n => n !== norma));
  };

  const handleKeyPressNormaManual = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      adicionarNormaManual();
    }
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
    const todasNormas = [...normasSelecionadas, ...normasManuais];
    const resposta = todasNormas.length > 0
      ? todasNormas.join(" | ")
      : "nenhuma";
    onConfirm(resposta);
  };

  const totalNormas = normasSelecionadas.length + normasManuais.length;
  const textoIntroducao = (dados as { texto_introducao?: string })?.texto_introducao;

  return (
    <div className="interface-container fade-in">
      {/* Texto de Introdução */}
      {textoIntroducao && (
        <div className="interface-intro" style={{
          marginBottom: '20px',
          padding: '16px',
          background: '#f8f9fa',
          borderRadius: '8px',
          borderLeft: '4px solid #1351B4',
          lineHeight: '1.8'
        }}>
          <div style={{ lineHeight: '1.8' }}>
            <ReactMarkdown>{textoIntroducao}</ReactMarkdown>
          </div>
        </div>
      )}

      {/* Cabeçalho */}
      <div className="interface-title">Normas e Dispositivos Legais</div>

      {/* Chips de normas selecionadas */}
      {totalNormas > 0 && (
        <div className="chips-container">
          <div className="chips-header">
            <span className="chips-count">
              {totalNormas} norma(s) selecionada(s)
            </span>
            <button className="btn-limpar-chips" onClick={limparSelecao} type="button">
              Limpar selecionadas
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
                  x
                </button>
              </div>
            ))}
            {normasManuais.map((norma, idx) => (
              <div key={`manual-${idx}`} className="chip chip-manual">
                <span className="chip-text">{norma}</span>
                <button
                  className="chip-remove"
                  onClick={() => removerNormaManual(norma)}
                  type="button"
                  aria-label="Remover norma"
                >
                  x
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="vertical-progressive-layout">

        {/* 1. LISTA DE NORMAS CADASTRADAS */}
        <div className="section-card section-biblioteca">
          <div className="section-header">
            <h3>Lista de normas cadastradas</h3>
            <p className="section-desc">Busque por tema ou nome da norma.</p>
          </div>

          <div className="search-container">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Buscar por nome, numero ou artigo da norma..."
              value={termoBusca}
              onChange={(e) => setTermoBusca(e.target.value)}
            />
            {termoBusca && (
              <button
                className="clear-search"
                onClick={() => setTermoBusca('')}
                type="button"
              >
                x
              </button>
            )}
          </div>

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

        {/* 2. ADICIONAR MANUALMENTE */}
        <div className="section-card section-manual">
          <div className="section-header">
            <h3>Adicionar norma manualmente</h3>
            <p className="section-desc">Informe normas que nao constam na lista acima.</p>
          </div>

          {!mostrarNormasManuais ? (
            <button
              className="btn-adicionar-manual"
              onClick={() => setMostrarNormasManuais(true)}
              type="button"
            >
              + Adicionar norma manualmente
            </button>
          ) : (
            <div className="campo-manual">
              <div className="campo-manual-input-group">
                <input
                  type="text"
                  className="campo-manual-input"
                  placeholder="Ex: Art. 34 da IN SGP n. 97/2022"
                  value={normaManualInput}
                  onChange={(e) => setNormaManualInput(e.target.value)}
                  onKeyDown={handleKeyPressNormaManual}
                  maxLength={300}
                />
                <button
                  className="btn-add"
                  onClick={adicionarNormaManual}
                  disabled={!normaManualInput.trim()}
                  type="button"
                >
                  + Adicionar
                </button>
              </div>
              <button
                className="btn-cancelar-manual"
                onClick={() => setMostrarNormasManuais(false)}
                type="button"
              >
                Fechar
              </button>
            </div>
          )}
        </div>

        {/* 3. SIGEPE LEGIS IA */}
        <div className="section-card section-legis">
          <div className="section-header">
            <h3>IA do Sigepe Legis</h3>
            <p className="section-desc">Ferramenta mantida pelo setor de legislacao para apoio na pesquisa de normas.</p>
          </div>

          <button
            className="btn-ia-legis"
            onClick={abrirIALegis}
            type="button"
          >
            Consultar IA do Sigepe Legis
          </button>
        </div>
      </div>

      {/* Rodape */}
      <div className="footer-actions">
        <button className="btn-interface btn-secondary" onClick={() => onConfirm('nao sei')}>
          Nao Sei
        </button>
        <button
          className="btn-interface btn-primary"
          onClick={handleConfirm}
          disabled={totalNormas === 0}
        >
          Confirmar {totalNormas > 0 && `(${totalNormas})`}
        </button>
      </div>

      <style>{`
        .interface-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1351B4;
          margin-bottom: 0.5rem;
          text-align: center;
        }

        /* ========== CHIPS ========== */
        .chips-container {
          margin-bottom: 1.5rem;
          padding: 1rem;
          background: #e8f5e9;
          border: 2px solid #66bb6a;
          border-radius: 12px;
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
        }

        .chip-manual {
          border-color: #ffc107;
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

        /* ========== LAYOUT ========== */
        .vertical-progressive-layout {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          margin-bottom: 1.5rem;
        }

        .section-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          border: 2px solid #e0e6ed;
        }

        .section-biblioteca {
          border-left: 4px solid #1351B4;
        }

        .section-manual {
          border-left: 4px solid #28a745;
        }

        .section-legis {
          border-left: 4px solid #667eea;
        }

        .section-header {
          margin-bottom: 1.25rem;
        }

        .section-header h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.1rem;
          color: #1351B4;
          font-weight: 600;
        }

        .section-desc {
          margin: 0;
          font-size: 0.85rem;
          color: #6c757d;
          line-height: 1.5;
        }

        /* ========== BUSCA ========== */
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
        }

        /* ========== ACORDEAO ========== */
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
        }

        .norma-card-small.selected {
          border-color: #28a745;
          background: #e8f5e9;
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

        /* ========== CAMPO MANUAL ========== */
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

        .campo-manual {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .campo-manual-input-group {
          display: flex;
          gap: 8px;
        }

        .campo-manual-input {
          flex: 1;
          padding: 10px 14px;
          border: 2px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
          transition: all 0.2s;
        }

        .campo-manual-input:focus {
          outline: none;
          border-color: #1351B4;
          background: #f8f9fa;
        }

        .btn-add {
          padding: 10px 20px;
          background: #28a745;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          white-space: nowrap;
        }

        .btn-add:hover:not(:disabled) {
          background: #218838;
        }

        .btn-add:disabled {
          background: #6c757d;
          cursor: not-allowed;
          opacity: 0.5;
        }

        .btn-cancelar-manual {
          padding: 0.5rem;
          background: transparent;
          color: #6c757d;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          font-size: 0.85rem;
          cursor: pointer;
        }

        .btn-cancelar-manual:hover {
          background: #f8f9fa;
        }

        /* ========== LEGIS ========== */
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

        /* ========== EMPTY STATE ========== */
        .empty-state {
          text-align: center;
          padding: 2rem;
          color: #6c757d;
          font-size: 0.9rem;
        }

        /* ========== FOOTER ========== */
        .footer-actions {
          margin-top: 2rem;
          padding-top: 1.5rem;
          border-top: 3px solid #1351B4;
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
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

        /* ========== MARKDOWN ========== */
        .interface-intro p {
          margin: 0 0 12px 0;
          line-height: 1.8;
        }

        .interface-intro strong {
          font-weight: 600;
          color: #1351B4;
        }

        .interface-intro ul, .interface-intro ol {
          margin: 8px 0 12px 20px;
          line-height: 1.8;
        }

        .interface-intro li {
          margin-bottom: 8px;
        }
      `}</style>
    </div>
  );
};

export default InterfaceNormas;
