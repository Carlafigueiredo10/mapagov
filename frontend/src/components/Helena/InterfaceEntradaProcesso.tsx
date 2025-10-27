import React, { useState, useMemo } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

interface AreaOrganizacional {
  codigo: string;
  nome_completo: string;
  nome_curto: string;
  prefixo: string;
  descricao?: string;
}

interface OrgaoCentralizado {
  sigla: string;
  nome_completo: string;
  observacao?: string;
}

interface InterfaceEntradaProcessoProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceEntradaProcesso: React.FC<InterfaceEntradaProcessoProps> = ({ dados, onConfirm }) => {
  const [origensSelecionadas, setOrigensSelecionadas] = useState<string[]>([]);
  const [grupoAberto, setGrupoAberto] = useState<string | null>(null);
  const [setorManual, setSetorManual] = useState<string>("");
  const [outraOrigemManual, setOutraOrigemManual] = useState<string>("");
  const [mostrarSetorManual, setMostrarSetorManual] = useState(false);
  const [mostrarOutraOrigem, setMostrarOutraOrigem] = useState(false);

  // Extrair dados do backend
  const areasOrganizacionais = useMemo(() => {
    const areas = (dados as { areas_organizacionais?: AreaOrganizacional[] })?.areas_organizacionais;
    return areas || [];
  }, [dados]);

  const orgaosCentralizados = useMemo(() => {
    const orgaos = (dados as { orgaos_centralizados?: OrgaoCentralizado[] })?.orgaos_centralizados;
    return orgaos || [];
  }, [dados]);

  // Grupos de origens
  const grupos = useMemo(() => {
    return {
      internas: {
        label: "📩 Origens Internas",
        itens: [
          ...areasOrganizacionais.map(area => ({
            id: `area_${area.codigo}`,
            label: `${area.nome_curto} (${area.codigo})`,
            descricao: area.descricao || area.nome_completo
          })),
          {
            id: "setor_manual",
            label: "Da sua própria coordenação-geral",
            descricao: "Digite o nome do setor"
          }
        ]
      },
      orgaos: {
        label: "🏛️ Órgãos Centralizados",
        itens: orgaosCentralizados.map(orgao => ({
          id: `orgao_${orgao.sigla}`,
          label: `${orgao.sigla} — ${orgao.nome_completo}`,
          descricao: orgao.observacao || ""
        }))
      },
      usuario: {
        label: "💬 Usuário / Requerente Direto",
        itens: [
          { id: "canal_sougov", label: "Canal SouGov", descricao: "Solicitações via SouGov" },
          { id: "protocolo_digital", label: "Protocolo Digital", descricao: "Processos digitais" },
          { id: "ouvidoria", label: "Ouvidoria", descricao: "Demandas da Ouvidoria" },
          { id: "0800", label: "0800", descricao: "Atendimento telefônico" },
          { id: "presencial", label: "Atendimento Presencial", descricao: "Presencial na DECIPEX" }
        ]
      },
      controle: {
        label: "⚖️ Órgãos de Controle",
        itens: [
          { id: "cgu_indicios", label: "CGU — Indícios", descricao: "Indícios de irregularidades" },
          { id: "cgu_atos", label: "CGU — Atos de Pessoal", descricao: "Análise de atos" },
          { id: "tcu_indicios", label: "TCU — Indícios", descricao: "Indícios de irregularidades" },
          { id: "tcu_acordaos", label: "TCU — Acórdãos", descricao: "Determinações via acórdão" },
          { id: "tcu_atos", label: "TCU — Atos de Pessoal", descricao: "Análise de atos" }
        ]
      },
      outra: {
        label: "📝 Outra Origem",
        itens: [
          { id: "outra_manual", label: "Descrever manualmente", descricao: "Campo aberto" }
        ]
      }
    };
  }, [areasOrganizacionais, orgaosCentralizados]);

  const toggleOrigem = (id: string, label: string) => {
    // Casos especiais
    if (id === "setor_manual") {
      setMostrarSetorManual(!mostrarSetorManual);
      return;
    }

    if (id === "outra_manual") {
      setMostrarOutraOrigem(!mostrarOutraOrigem);
      return;
    }

    // Seleção normal
    setOrigensSelecionadas(prev =>
      prev.includes(label)
        ? prev.filter(o => o !== label)
        : [...prev, label]
    );
  };

  const toggleGrupo = (grupo: string) => {
    setGrupoAberto(prev => (prev === grupo ? null : grupo));
  };

  const limparSelecao = () => {
    setOrigensSelecionadas([]);
    setSetorManual("");
    setOutraOrigemManual("");
    setMostrarSetorManual(false);
    setMostrarOutraOrigem(false);
  };

  const handleConfirm = () => {
    const todasOrigens = [...origensSelecionadas];

    if (setorManual.trim()) {
      todasOrigens.push(`Setor: ${setorManual.trim()}`);
    }

    if (outraOrigemManual.trim()) {
      todasOrigens.push(outraOrigemManual.trim());
    }

    const resposta = todasOrigens.length > 0
      ? todasOrigens.join(" | ")
      : "nenhuma";

    onConfirm(resposta);
  };

  return (
    <div className="interface-container fade-in">
      {/* Cabeçalho */}
      <div className="interface-title">📥 Entrada do Processo</div>
      <div className="interface-subtitle">
        Toda atividade tem um "ponto de partida". Me conta, de onde costuma vir o processo que você executa?
      </div>

      {/* Chips de Origens Selecionadas */}
      {origensSelecionadas.length > 0 && (
        <div className="chips-container">
          <div className="chips-header">
            <span className="chips-count">{origensSelecionadas.length} origem(ns) selecionada(s) ✅</span>
            <button className="btn-limpar-chips" onClick={limparSelecao} type="button">
              Limpar todas
            </button>
          </div>
          <div className="chips-list">
            {origensSelecionadas.map((origem, idx) => (
              <div key={idx} className="chip">
                <span className="chip-text">{origem}</span>
                <button
                  className="chip-remove"
                  onClick={() => toggleOrigem(origem, origem)}
                  type="button"
                  aria-label="Remover origem"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grupos Expansíveis */}
      <div className="grupos-container">
        {Object.entries(grupos).map(([grupoKey, grupo]) => (
          <div key={grupoKey} className="grupo-card">
            <div
              className="grupo-header"
              onClick={() => toggleGrupo(grupoKey)}
            >
              {grupoAberto === grupoKey ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
              <span className="grupo-label">{grupo.label}</span>
              <span className="grupo-count">({grupo.itens.length})</span>
            </div>

            {grupoAberto === grupoKey && (
              <div className="grupo-conteudo">
                {grupo.itens.map((item) => {
                  const isSelected = origensSelecionadas.includes(item.label);
                  const isSetorManual = item.id === "setor_manual";
                  const isOutraManual = item.id === "outra_manual";

                  return (
                    <div key={item.id}>
                      <div
                        className={`origem-card ${isSelected ? 'selected' : ''}`}
                        onClick={() => toggleOrigem(item.id, item.label)}
                      >
                        <input
                          type="checkbox"
                          readOnly
                          checked={isSelected || (isSetorManual && mostrarSetorManual) || (isOutraManual && mostrarOutraOrigem)}
                        />
                        <div className="origem-info">
                          <strong>{item.label}</strong>
                          {item.descricao && <small>{item.descricao}</small>}
                        </div>
                      </div>

                      {/* Campo manual: Setor */}
                      {isSetorManual && mostrarSetorManual && (
                        <div className="input-manual-container">
                          <input
                            type="text"
                            className="input-manual"
                            placeholder="Ex: Divisão de Aposentadorias"
                            value={setorManual}
                            onChange={(e) => setSetorManual(e.target.value)}
                            maxLength={200}
                          />
                        </div>
                      )}

                      {/* Campo manual: Outra Origem */}
                      {isOutraManual && mostrarOutraOrigem && (
                        <div className="input-manual-container">
                          <input
                            type="text"
                            className="input-manual"
                            placeholder="Ex: Demanda interna de auditoria"
                            value={outraOrigemManual}
                            onChange={(e) => setOutraOrigemManual(e.target.value)}
                            maxLength={300}
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Rodapé */}
      <div className="footer-actions">
        <button className="btn-interface btn-secondary" onClick={() => onConfirm('nao sei')}>
          Não Sei
        </button>
        <button
          className="btn-interface btn-primary"
          onClick={handleConfirm}
          disabled={origensSelecionadas.length === 0 && !setorManual.trim() && !outraOrigemManual.trim()}
        >
          Confirmar {origensSelecionadas.length > 0 && `(${origensSelecionadas.length})`}
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

        /* ========== CHIPS CONTAINER ========== */
        .chips-container {
          margin-bottom: 1.5rem;
          padding: 1rem;
          background: linear-gradient(135deg, #e3f2fd 0%, #e1f5fe 100%);
          border: 2px solid #1976d2;
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
          color: #0d47a1;
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
          border: 1px solid #1976d2;
          border-radius: 20px;
          font-size: 0.85rem;
          max-width: 100%;
          transition: all 0.2s;
        }

        .chip:hover {
          box-shadow: 0 2px 8px rgba(25, 118, 210, 0.3);
        }

        .chip-text {
          flex: 1;
          color: #0d47a1;
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

        /* ========== GRUPOS CONTAINER ========== */
        .grupos-container {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .grupo-card {
          background: white;
          border: 2px solid #e0e6ed;
          border-radius: 12px;
          overflow: hidden;
          transition: all 0.3s;
        }

        .grupo-card:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .grupo-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem 1.25rem;
          background: #f8f9fa;
          cursor: pointer;
          transition: all 0.2s;
        }

        .grupo-header:hover {
          background: #e9ecef;
        }

        .grupo-label {
          flex: 1;
          font-weight: 600;
          color: #495057;
          font-size: 1rem;
        }

        .grupo-count {
          font-weight: 400;
          color: #6c757d;
          font-size: 0.85rem;
        }

        .grupo-conteudo {
          padding: 1rem;
          background: white;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        /* ========== ORIGEM CARD ========== */
        .origem-card {
          display: flex;
          gap: 0.75rem;
          padding: 0.9rem;
          background: #f8f9fa;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .origem-card:hover {
          border-color: #1351B4;
          background: #f0f4ff;
          transform: translateX(4px);
        }

        .origem-card.selected {
          border-color: #1976d2;
          background: linear-gradient(135deg, #e3f2fd 0%, #e1f5fe 100%);
          animation: selectedPulse 0.3s ease-in;
        }

        @keyframes selectedPulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.02); }
          100% { transform: scale(1); }
        }

        .origem-card input[type="checkbox"] {
          margin-top: 0.25rem;
          cursor: pointer;
        }

        .origem-info {
          flex: 1;
        }

        .origem-info strong {
          color: #1351B4;
          font-size: 0.95rem;
          display: block;
        }

        .origem-info small {
          display: block;
          color: #6c757d;
          font-size: 0.8rem;
          margin-top: 0.25rem;
        }

        /* ========== INPUT MANUAL ========== */
        .input-manual-container {
          margin-top: 0.5rem;
          padding: 0.75rem;
          background: #fff3cd;
          border: 2px dashed #ffc107;
          border-radius: 8px;
          animation: fadeIn 0.3s ease-in;
        }

        .input-manual {
          width: 100%;
          padding: 0.75rem;
          border: 2px solid #ffc107;
          border-radius: 6px;
          font-size: 0.95rem;
          transition: all 0.2s;
        }

        .input-manual:focus {
          outline: none;
          border-color: #ff9800;
          box-shadow: 0 0 0 3px rgba(255, 152, 0, 0.1);
        }

        .input-manual::placeholder {
          color: #adb5bd;
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
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.95rem;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
        }

        .btn-primary {
          background: #1976d2;
          color: white;
        }

        .btn-primary:hover {
          background: #1565c0;
        }

        .btn-primary:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        @media (max-width: 768px) {
          .footer-actions {
            flex-direction: column;
          }

          .btn-interface {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default InterfaceEntradaProcesso;
