import React, { useState } from "react";

interface DropdownArquiteturaProps {
  tipo: string;
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const DropdownArquitetura: React.FC<DropdownArquiteturaProps> = ({ tipo, dados, onConfirm }) => {
  const [selecao, setSelecao] = useState<string>("");
  const [textoLivre, setTextoLivre] = useState<string>("");
  const [modoTextoLivre, setModoTextoLivre] = useState<boolean>(false);

  // Extrair dados
  const opcoes = (dados?.opcoes as string[]) || [];
  const titulo = (dados?.titulo as string) || "Selecione uma opção";
  const permitirTextoLivre = (dados?.permitir_texto_livre as boolean) || false;

  // Mapear tipo para label
  const tipoLabels: Record<string, string> = {
    dropdown_macro: "Macroprocesso",
    dropdown_processo: "Processo",
    dropdown_subprocesso: "Subprocesso",
    dropdown_atividade: "Atividade",
    dropdown_processo_com_texto_livre: "Processo",
    dropdown_subprocesso_com_texto_livre: "Subprocesso",
    dropdown_atividade_com_texto_livre: "Atividade",
  };

  const label = tipoLabels[tipo] || "Opção";

  const handleConfirm = () => {
    const resposta = modoTextoLivre ? textoLivre.trim() : selecao;

    if (!resposta) {
      alert(`Por favor, selecione ou digite um ${label.toLowerCase()}.`);
      return;
    }
    onConfirm(resposta);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">📋 {titulo}</div>
      <div className="interface-content">
        {!modoTextoLivre ? (
          <>
            <label htmlFor="dropdown-select" style={{ display: "block", marginBottom: "8px", fontWeight: 500 }}>
              {label}:
            </label>
            <select
              id="dropdown-select"
              value={selecao}
              onChange={(e) => setSelecao(e.target.value)}
              disabled={modoTextoLivre}
              style={{
                width: "100%",
                padding: "10px",
                fontSize: "14px",
                border: "1px solid #d1d5db",
                borderRadius: "8px",
                backgroundColor: "#fff",
                cursor: "pointer",
              }}
            >
              <option value="">-- Selecione --</option>
              {opcoes.map((opcao, idx) => (
                <option key={idx} value={opcao}>
                  {opcao}
                </option>
              ))}
            </select>
          </>
        ) : (
          <>
            <label htmlFor="texto-livre" style={{ display: "block", marginBottom: "8px", fontWeight: 500 }}>
              Digite o {label.toLowerCase()}:
            </label>
            <input
              id="texto-livre"
              type="text"
              value={textoLivre}
              onChange={(e) => setTextoLivre(e.target.value)}
              placeholder={`Digite o ${label.toLowerCase()}...`}
              style={{
                width: "100%",
                padding: "10px",
                fontSize: "14px",
                border: "1px solid #d1d5db",
                borderRadius: "8px",
                backgroundColor: "#fff",
              }}
            />
          </>
        )}

        {permitirTextoLivre && (
          <div style={{ marginTop: "12px", textAlign: "center" }}>
            <button
              onClick={() => {
                setModoTextoLivre(!modoTextoLivre);
                setSelecao("");
                setTextoLivre("");
              }}
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                color: "#6366f1",
                background: "transparent",
                border: "1px solid #6366f1",
                borderRadius: "6px",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              {modoTextoLivre ? "↩️ Voltar para lista" : "✏️ Digitar manualmente"}
            </button>
          </div>
        )}
      </div>
      <div className="action-buttons">
        <button
          className="btn-interface btn-secondary"
          onClick={() => {
            // Chamar modal de ajuda da Helena
            if (dados && typeof dados === 'object' && 'onPedirAjuda' in dados) {
              const onPedirAjuda = dados.onPedirAjuda as () => void;
              onPedirAjuda();
            }
          }}
          style={{
            marginRight: "8px",
            backgroundColor: "#f59e0b",
            color: "white",
          }}
        >
          🆘 Preciso de Ajuda
        </button>
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar
        </button>
      </div>
    </div>
  );
};

export default DropdownArquitetura;
