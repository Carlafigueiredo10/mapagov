import React, { useState } from "react";
import { Plus, Trash2, Edit2 } from "lucide-react";

interface Documento {
  tipo_documento: string;
  tipo_uso: string;
  obrigatorio: boolean;
  descricao: string;
  sistema: string | null;
}

interface InterfaceDocumentosProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceDocumentos: React.FC<InterfaceDocumentosProps> = ({ onConfirm }) => {
  const [documentos, setDocumentos] = useState<Documento[]>([]);
  const [editandoIndex, setEditandoIndex] = useState<number | null>(null);

  // Formulário atual
  const [tipoDocumento, setTipoDocumento] = useState<string>("Formulário");
  const [tipoUso, setTipoUso] = useState<string>("Gerado");
  const [obrigatorio, setObrigatorio] = useState<boolean>(true);
  const [descricao, setDescricao] = useState<string>("");
  const [sistema, setSistema] = useState<string>("");

  const tiposDocumento = [
    "Formulário",
    "Despacho",
    "Ofício",
    "Nota Informativa",
    "Nota Técnica",
    "Tela de sistema",
    "Documentos Pessoais"
  ];

  const adicionarDocumento = () => {
    // Validação
    if (!descricao.trim()) {
      alert("Por favor, preencha a descrição do documento.");
      return;
    }

    if (tipoDocumento === "Tela de sistema" && !sistema.trim()) {
      alert("Para 'Tela de sistema', por favor informe qual sistema.");
      return;
    }

    const novoDocumento: Documento = {
      tipo_documento: tipoDocumento,
      tipo_uso: tipoUso,
      obrigatorio: obrigatorio,
      descricao: descricao.trim(),
      sistema: tipoDocumento === "Tela de sistema" ? sistema.trim() : null
    };

    if (editandoIndex !== null) {
      // Editando documento existente
      const novosDocumentos = [...documentos];
      novosDocumentos[editandoIndex] = novoDocumento;
      setDocumentos(novosDocumentos);
      setEditandoIndex(null);
    } else {
      // Adicionando novo
      setDocumentos([...documentos, novoDocumento]);
    }

    // Limpar formulário
    limparFormulario();
  };

  const limparFormulario = () => {
    setTipoDocumento("Formulário");
    setTipoUso("Gerado");
    setObrigatorio(true);
    setDescricao("");
    setSistema("");
  };

  const editarDocumento = (index: number) => {
    const doc = documentos[index];
    setTipoDocumento(doc.tipo_documento);
    setTipoUso(doc.tipo_uso);
    setObrigatorio(doc.obrigatorio);
    setDescricao(doc.descricao);
    setSistema(doc.sistema || "");
    setEditandoIndex(index);
  };

  const removerDocumento = (index: number) => {
    setDocumentos(documentos.filter((_, i) => i !== index));
  };

  const cancelarEdicao = () => {
    setEditandoIndex(null);
    limparFormulario();
  };

  const handleConfirm = () => {
    if (documentos.length === 0) {
      alert("Por favor, adicione pelo menos um documento.");
      return;
    }

    // Enviar como JSON
    const respostaJSON = JSON.stringify(documentos);
    onConfirm(respostaJSON);
  };

  const handlePular = () => {
    onConfirm("[]"); // Lista vazia
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">📄 Documentos, Formulários e Modelos</div>

      {/* Formulário */}
      <div className="form-documento">
        <div className="form-header">
          <h3>{editandoIndex !== null ? "Editar Documento" : "Adicionar Documento"}</h3>
        </div>

        <div className="form-grid">
          <div className="form-group">
            <label>Tipo do Documento *</label>
            <select
              value={tipoDocumento}
              onChange={(e) => setTipoDocumento(e.target.value)}
              className="form-select"
            >
              {tiposDocumento.map(tipo => (
                <option key={tipo} value={tipo}>{tipo}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Tipo *</label>
            <div className="radio-group">
              <label className="radio-label">
                <input
                  type="radio"
                  value="Gerado"
                  checked={tipoUso === "Gerado"}
                  onChange={(e) => setTipoUso(e.target.value)}
                />
                Gerado
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  value="Utilizado"
                  checked={tipoUso === "Utilizado"}
                  onChange={(e) => setTipoUso(e.target.value)}
                />
                Utilizado
              </label>
            </div>
          </div>

          <div className="form-group">
            <label>Obrigatório *</label>
            <div className="radio-group">
              <label className="radio-label">
                <input
                  type="radio"
                  checked={obrigatorio === true}
                  onChange={() => setObrigatorio(true)}
                />
                Sim
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  checked={obrigatorio === false}
                  onChange={() => setObrigatorio(false)}
                />
                Não
              </label>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label>Descrição do Documento *</label>
          <input
            type="text"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            placeholder="Ex: Requerimento de auxílio-saúde assinado"
            className="form-input"
          />
        </div>

        {tipoDocumento === "Tela de sistema" && (
          <div className="form-group">
            <label>Qual Sistema? *</label>
            <input
              type="text"
              value={sistema}
              onChange={(e) => setSistema(e.target.value)}
              placeholder="Ex: SIAPE, SEI, SIGEP"
              className="form-input"
            />
          </div>
        )}

        <div className="form-actions">
          {editandoIndex !== null && (
            <button
              className="btn-form btn-cancel"
              onClick={cancelarEdicao}
              type="button"
            >
              Cancelar
            </button>
          )}
          <button
            className="btn-form btn-add"
            onClick={adicionarDocumento}
            type="button"
          >
            <Plus size={18} />
            {editandoIndex !== null ? "Salvar Alterações" : "Adicionar Documento"}
          </button>
        </div>
      </div>

      {/* Lista de Documentos */}
      {documentos.length > 0 && (
        <div className="documentos-lista">
          <h3>📋 Documentos Adicionados ({documentos.length})</h3>
          {documentos.map((doc, index) => (
            <div key={index} className="documento-item">
              <div className="documento-info">
                <div className="documento-tipo">{doc.tipo_documento}</div>
                <div className="documento-descricao">{doc.descricao}</div>
                <div className="documento-tags">
                  <span className={`tag ${doc.tipo_uso === 'Gerado' ? 'tag-gerado' : 'tag-utilizado'}`}>
                    {doc.tipo_uso}
                  </span>
                  <span className={`tag ${doc.obrigatorio ? 'tag-obrigatorio' : 'tag-opcional'}`}>
                    {doc.obrigatorio ? 'Obrigatório' : 'Opcional'}
                  </span>
                  {doc.sistema && (
                    <span className="tag tag-sistema">Sistema: {doc.sistema}</span>
                  )}
                </div>
              </div>
              <div className="documento-actions">
                <button
                  className="btn-icon btn-edit"
                  onClick={() => editarDocumento(index)}
                  title="Editar"
                >
                  <Edit2 size={16} />
                </button>
                <button
                  className="btn-icon btn-delete"
                  onClick={() => removerDocumento(index)}
                  title="Remover"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Ações Finais */}
      <div className="action-buttons">
        <button className="btn-interface btn-secondary" onClick={handlePular}>
          Pular (sem documentos)
        </button>
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar ({documentos.length} documento{documentos.length !== 1 ? 's' : ''})
        </button>
      </div>

      <style>{`
        .form-documento {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 1.5rem;
          margin: 1.5rem 0;
        }

        .form-header h3 {
          margin: 0 0 1rem 0;
          color: #495057;
          font-size: 1rem;
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group label {
          font-size: 0.9rem;
          font-weight: 500;
          color: #495057;
        }

        .form-select,
        .form-input {
          padding: 0.6rem;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 0.9rem;
        }

        .form-select:focus,
        .form-input:focus {
          outline: none;
          border-color: #80bdff;
          box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
        }

        .radio-group {
          display: flex;
          gap: 1rem;
        }

        .radio-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          font-weight: normal;
        }

        .radio-label input[type="radio"] {
          cursor: pointer;
        }

        .form-actions {
          display: flex;
          gap: 0.75rem;
          justify-content: flex-end;
          margin-top: 1rem;
        }

        .btn-form {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.6rem 1.2rem;
          border: none;
          border-radius: 4px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-add {
          background: #28a745;
          color: white;
        }

        .btn-add:hover {
          background: #218838;
        }

        .btn-cancel {
          background: #6c757d;
          color: white;
        }

        .btn-cancel:hover {
          background: #5a6268;
        }

        .documentos-lista {
          margin: 1.5rem 0;
        }

        .documentos-lista h3 {
          margin-bottom: 1rem;
          color: #495057;
          font-size: 1rem;
        }

        .documento-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          margin-bottom: 0.75rem;
        }

        .documento-info {
          flex: 1;
        }

        .documento-tipo {
          font-weight: 600;
          color: #1351B4;
          margin-bottom: 0.25rem;
        }

        .documento-descricao {
          color: #495057;
          margin-bottom: 0.5rem;
        }

        .documento-tags {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .tag {
          padding: 0.25rem 0.6rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .tag-gerado {
          background: #d1ecf1;
          color: #0c5460;
        }

        .tag-utilizado {
          background: #fff3cd;
          color: #856404;
        }

        .tag-obrigatorio {
          background: #f8d7da;
          color: #721c24;
        }

        .tag-opcional {
          background: #d4edda;
          color: #155724;
        }

        .tag-sistema {
          background: #e2e3e5;
          color: #383d41;
        }

        .documento-actions {
          display: flex;
          gap: 0.5rem;
        }

        .btn-icon {
          padding: 0.5rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .btn-edit {
          background: #17a2b8;
          color: white;
        }

        .btn-edit:hover {
          background: #138496;
        }

        .btn-delete {
          background: #dc3545;
          color: white;
        }

        .btn-delete:hover {
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
      `}</style>
    </div>
  );
};

export default InterfaceDocumentos;