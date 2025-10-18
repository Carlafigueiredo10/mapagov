import React, { useState, useMemo } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

interface Norma {
  nome_curto: string;
  nome_completo: string;
  artigos: string;
  confianca?: number;
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


  // Extrair sugestões do backend (top 3)
  const sugestoes = useMemo(() => {
    const sugestoesDados = (dados as { sugestoes?: Norma[] })?.sugestoes;
    if (sugestoesDados && Array.isArray(sugestoesDados)) {
      return sugestoesDados;
    }
    return [];
  }, [dados]);

  // Organizar normas por categoria (hardcoded - ideal seria vir do backend)
  const categorias = useMemo(() => {
    return {
      "Assistência à Saúde": [
        { nome_curto: "IN 97/2022", nome_completo: "Instrução Normativa SGP/SEDGG/ME nº 97, de 26 de dezembro de 2022", artigos: "Art. 34-42" },
        { nome_curto: "Lei 8112/90", nome_completo: "Lei nº 8.112, de 11 de dezembro de 1990", artigos: "Art. 230" },
        { nome_curto: "Decreto 4978/2004", nome_completo: "Decreto nº 4.978, de 3 de fevereiro de 2004", artigos: "Todos" }
      ],
      "Pagamento e Folha": [
        { nome_curto: "IN 02/2018", nome_completo: "Instrução Normativa SEGES/MPDG nº 2, de 30 de março de 2018", artigos: "Todos" },
        { nome_curto: "Lei 10520/2002", nome_completo: "Lei nº 10.520, de 17 de julho de 2002", artigos: "Todos" }
      ],
      "Processo Administrativo": [
        { nome_curto: "Lei 9784/99", nome_completo: "Lei nº 9.784, de 29 de janeiro de 1999", artigos: "Todos" },
        { nome_curto: "Decreto 9094/2017", nome_completo: "Decreto nº 9.094, de 17 de julho de 2017", artigos: "Todos" }
      ],
      "Gestão Financeira": [
        { nome_curto: "Lei 4320/64", nome_completo: "Lei nº 4.320, de 17 de março de 1964", artigos: "Todos" },
        { nome_curto: "LRF", nome_completo: "Lei Complementar nº 101, de 4 de maio de 2000", artigos: "Todos" }
      ],
      "Gestão de Pessoas": [
        { nome_curto: "Lei 8112/90 - Capacitação", nome_completo: "Lei nº 8.112, de 11 de dezembro de 1990", artigos: "Art. 87-101" },
        { nome_curto: "Decreto 9991/2019", nome_completo: "Decreto nº 9.991, de 28 de agosto de 2019", artigos: "Todos" }
      ],
      "Proteção de Dados": [
        { nome_curto: "LGPD", nome_completo: "Lei nº 13.709, de 14 de agosto de 2018", artigos: "Todos" },
        { nome_curto: "Decreto 10046/2019", nome_completo: "Decreto nº 10.046, de 9 de outubro de 2019", artigos: "Todos" }
      ],
      "Licitações e Contratos": [
        { nome_curto: "Lei 14133/2021", nome_completo: "Lei nº 14.133, de 1º de abril de 2021", artigos: "Todos" },
        { nome_curto: "Lei 8666/93", nome_completo: "Lei nº 8.666, de 21 de junho de 1993", artigos: "Todos" }
      ],
      "Governança e Riscos": [
        { nome_curto: "IN Conjunta 01/2016", nome_completo: "Instrução Normativa Conjunta CGU/MP nº 01, de 10 de maio de 2016", artigos: "Todos" },
        { nome_curto: "Decreto 9203/2017", nome_completo: "Decreto nº 9.203, de 22 de novembro de 2017", artigos: "Todos" }
      ],
      "Transparência": [
        { nome_curto: "LAI", nome_completo: "Lei nº 12.527, de 18 de novembro de 2011", artigos: "Todos" },
        { nome_curto: "Decreto 7724/2012", nome_completo: "Decreto nº 7.724, de 16 de maio de 2012", artigos: "Todos" }
      ],
      "Integridade e Compliance": [
        { nome_curto: "Lei Anticorrupção", nome_completo: "Lei nº 12.846, de 1º de agosto de 2013", artigos: "Todos" },
        { nome_curto: "Decreto 8420/2015", nome_completo: "Decreto nº 8.420, de 18 de março de 2015", artigos: "Todos" }
      ]
    };
  }, []);

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

  const handleConfirm = () => {
    // Combinar normas selecionadas + normas manuais (filtrar vazias)
    const normsManuaisPreenchidas = normasManuais.filter(n => n.trim().length > 0);
    const todasNormas = [...normasSelecionadas, ...normsManuaisPreenchidas];

    const resposta = todasNormas.length > 0
      ? todasNormas.join(" | ")
      : "nenhuma";
    onConfirm(resposta);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">📚 Normas e Dispositivos Legais</div>

      {/* Sugestões (Top 3) */}
      {sugestoes.length > 0 && (
        <div className="sugestoes-section">
          <div className="sugestoes-header">
            <h3>Sugestões para este processo:</h3>
            <button
              className="btn-selecionar-sugestoes"
              onClick={selecionarTodasSugestoes}
              type="button"
            >
              Selecionar Todas as Sugestões
            </button>
          </div>

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
        </div>
      )}

      {/* Botão Visualizar Mais */}
      <div className="visualizar-mais-section">
        <button
          className="btn-visualizar-mais"
          onClick={() => setMostrarTodas(!mostrarTodas)}
          type="button"
        >
          {mostrarTodas ? '▲ Ocultar outras normas' : '▼ Visualizar todas as normas disponíveis'}
        </button>
      </div>

      {/* Acordeão de Categorias */}
      {mostrarTodas && (
        <div className="categorias-acordeao">
          {Object.entries(categorias).map(([categoria, normas]) => (
            <div key={categoria} className="categoria-item">
              <div
                className="categoria-header"
                onClick={() => toggleCategoria(categoria)}
              >
                {categoriaAberta === categoria ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                <span>{categoria} ({normas.length})</span>
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
      )}

      {/* Botão: Não Encontrei a Norma */}
      {!mostrarNormasManuais && (
        <div className="nao-encontrei-section">
          <button
            className="btn-nao-encontrei"
            onClick={() => setMostrarNormasManuais(true)}
            type="button"
          >
            ⚠️ Não encontrei a norma da minha atividade
          </button>
        </div>
      )}

      {/* Seção de Normas Manuais + IA Legis (Expansível) */}
      {mostrarNormasManuais && (
        <div className="normas-manuais-section">
          <div className="normas-manuais-header">
            <h3>💡 Não encontrou a norma que procura?</h3>
          </div>

          <button
            className="btn-ia-legis"
            onClick={abrirIALegis}
            type="button"
          >
            🤖 Consultar IA Legis (Sigepe)
          </button>

          <div className="normas-manuais-descricao">
            Ou adicione manualmente:
          </div>

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
              {normasManuais.length > 1 && (
                <button
                  className="btn-remover-norma"
                  onClick={() => removerCampoNormaManual(index)}
                  type="button"
                  title="Remover norma"
                >
                  ✕
                </button>
              )}
            </div>
          ))}

          <button
            className="btn-adicionar-norma"
            onClick={adicionarCampoNormaManual}
            type="button"
          >
            ➕ Adicionar Outra Norma
          </button>
        </div>
      )}

      {/* Contador e Limpar */}
      <div className="contador-e-limpar">
        <div className="contador-normas">
          {normasSelecionadas.length} norma(s) selecionada(s)
        </div>
        {normasSelecionadas.length > 0 && (
          <button
            className="btn-limpar-selecao"
            onClick={limparSelecao}
            type="button"
          >
            🗑️ Limpar Seleção
          </button>
        )}
      </div>

      {/* Ações */}
      <div className="action-buttons">
        <button className="btn-interface btn-secondary" onClick={() => onConfirm('nao sei')}>
          Não Sei
        </button>
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar
        </button>
      </div>

      <style>{`
        .sugestoes-section {
          margin: 1.5rem 0;
          padding: 1rem;
          background: #f0f4ff;
          border-radius: 8px;
          border: 2px solid #1351B4;
        }

        .sugestoes-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .sugestoes-header h3 {
          margin: 0;
          font-size: 1rem;
          color: #1351B4;
        }

        .btn-selecionar-sugestoes {
          padding: 0.5rem 1rem;
          background: #1351B4;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.85rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-selecionar-sugestoes:hover {
          background: #0d3a85;
        }

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
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .norma-card:hover {
          border-color: #1351B4;
          box-shadow: 0 2px 8px rgba(19, 81, 180, 0.1);
        }

        .norma-card.selected {
          border-color: #1351B4;
          background: #e8f0ff;
        }

        .norma-card input[type="checkbox"] {
          margin-top: 0.25rem;
          cursor: pointer;
        }

        .norma-info {
          flex: 1;
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
          gap: 0.5rem;
          padding: 1rem;
          background: #f8f9fa;
          cursor: pointer;
          transition: background 0.2s;
        }

        .categoria-header:hover {
          background: #e9ecef;
        }

        .categoria-header span {
          font-weight: 600;
          color: #495057;
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
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .norma-card-small:hover {
          border-color: #1351B4;
          background: #f0f4ff;
        }

        .norma-card-small.selected {
          border-color: #1351B4;
          background: #e8f0ff;
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
          margin: 2rem 0;
          padding: 1.5rem;
          background: #fff9e6;
          border: 2px solid #ffc107;
          border-radius: 8px;
        }

        .normas-manuais-header h3 {
          margin: 0 0 1rem 0;
          color: #856404;
          font-size: 1rem;
          text-align: center;
        }

        .btn-ia-legis {
          width: 100%;
          padding: 1rem;
          background: linear-gradient(135deg, #6f42c1, #5a32a3);
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
          box-shadow: 0 4px 12px rgba(111, 66, 193, 0.3);
          margin-bottom: 1rem;
        }

        .btn-ia-legis:hover {
          background: linear-gradient(135deg, #5a32a3, #4a2a8a);
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(111, 66, 193, 0.4);
        }

        .normas-manuais-descricao {
          text-align: center;
          color: #856404;
          font-weight: 500;
          margin: 1rem 0 0.75rem 0;
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
          transition: border-color 0.2s;
        }

        .norma-manual-input:focus {
          outline: none;
          border-color: #ffc107;
          box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.1);
        }

        .norma-manual-input::placeholder {
          color: #adb5bd;
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

        .btn-adicionar-norma {
          width: 100%;
          padding: 0.75rem;
          border: 2px dashed #28a745;
          background: white;
          color: #28a745;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.95rem;
          font-weight: 500;
          transition: all 0.2s;
          margin-top: 0.5rem;
        }

        .btn-adicionar-norma:hover {
          background: #28a745;
          color: white;
          border-style: solid;
        }
      `}</style>
    </div>
  );
};

export default InterfaceNormas;