import { useState } from "react";
import styles from "./DocumentosForm.module.css";

interface Documento {
  tipo: string;
  origem: string;
  detalhes: string;
  animating?: boolean;
}

interface TipoDocumento {
  tipo: string;
  ordem: number;
  hint: string;
  descricao?: string;
}

interface DocumentosFormProps {
  onSubmit: (documentos: Documento[]) => void;
  instrucoes?: string;
  tipos_documentos?: TipoDocumento[];
}

export function DocumentosForm({ onSubmit, instrucoes, tipos_documentos }: DocumentosFormProps) {
  const [documentos, setDocumentos] = useState<Documento[]>([]);
  const [form, setForm] = useState({ tipo: "", origem: "", detalhes: "" });
  const [recentlyAdded, setRecentlyAdded] = useState(false);

  // Lista padrão caso não venha do backend
  const tiposDoc = tipos_documentos || [
    { tipo: 'Formulário', ordem: 1, hint: 'Ex.: CPF, Matrícula SIAPE, Período, Anexos obrigatórios' },
    { tipo: 'Despacho', ordem: 2, hint: 'Descreva o tipo de decisão ou encaminhamento' },
    { tipo: 'Ofício', ordem: 3, hint: 'Descreva o assunto do ofício' },
    { tipo: 'Nota Técnica', ordem: 4, hint: 'Descreva o assunto principal da nota' },
    { tipo: 'Nota Informativa', ordem: 5, hint: 'Descreva o conteúdo informado' },
    { tipo: 'Tela de sistema', ordem: 6, hint: 'Ex.: SouGov › Consulta de Dependentes' },
    { tipo: 'Outro', ordem: 7, hint: 'Especifique qual tipo de documento' }
  ];

  // Encontrar hint para o tipo selecionado
  const getHintForTipo = (tipo: string) => {
    const tipoEncontrado = tiposDoc.find(t => t.tipo === tipo);
    return tipoEncontrado?.hint || "Detalhamento (ex: campos principais, assunto...)";
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = () => {
    if (!form.tipo) {
      alert("Por favor, preencha pelo menos o tipo de documento.");
      return;
    }

    const novoDoc: Documento = { ...form, animating: true };
    setDocumentos((prev) => [...prev, novoDoc]);
    setForm({ tipo: "", origem: "", detalhes: "" });
    setRecentlyAdded(true);

    // Remove o estado de animação após 600ms
    setTimeout(() => {
      setDocumentos((prev) =>
        prev.map((d) => ({ ...d, animating: false }))
      );
      setRecentlyAdded(false);
    }, 600);
  };

  const handleFinish = () => {
    // Enviar lista de documentos para backend (será empacotado no InterfaceDinamica)
    const documentosSemAnimacao = documentos.map(({ animating, ...doc }) => doc);
    onSubmit(documentosSemAnimacao);
  };

  const handleRemove = (index: number) => {
    setDocumentos((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <form aria-labelledby="documentosFormTitle" className={styles.formularioDocumentos}>
      <h2 id="documentosFormTitle" className={styles.tituloForm}>
        🗂️ Documentos, Formulários e Modelos
      </h2>

      <p className={styles.introducao}>
        Agora vamos detalhar os documentos, formulários e modelos que fazem parte desta atividade.
        Pra ficar claro e organizado, vamos pensar por etapas, tudo bem?
      </p>

      {/* Linha com 3 colunas */}
      <div className={styles.docRow}>
        <select
          name="tipo"
          value={form.tipo}
          onChange={handleChange}
          aria-label="Tipo de documento"
          required
        >
          <option value="">Tipo de documento</option>
          {tiposDoc.map((td) => (
            <option key={td.tipo} value={td.tipo}>
              {td.tipo}
            </option>
          ))}
        </select>

        <select
          name="origem"
          value={form.origem}
          onChange={handleChange}
          aria-label="Origem do documento"
          required
        >
          <option value="">Origem</option>
          <option value="recebido">Requerido (vem de fora)</option>
          <option value="gerado">Gerado pela equipe</option>
        </select>

        <input
          type="text"
          name="detalhes"
          value={form.detalhes}
          onChange={handleChange}
          placeholder={getHintForTipo(form.tipo)}
          aria-label="Detalhamento do documento"
        />
      </div>

      {/* Botões */}
      <div className={styles.botoes}>
        <button
          type="button"
          className={styles.btnPrimario}
          onClick={handleAdd}
          aria-label="Confirmar e adicionar outro documento"
        >
          ✅ Confirmar e adicionar outro
        </button>
        <button
          type="button"
          className={styles.btnSecundario}
          onClick={handleFinish}
          aria-label="Encerrar lista de documentos"
        >
          🚪 Encerrar lista
        </button>
      </div>

      {/* Dica rodapé */}
      <p className={styles.dica}>
        <strong>Dica:</strong> use palavras simples e objetivas. Se tiver dúvida, pode registrar o essencial e voltar depois para completar.
      </p>

      {/* Lista de documentos adicionados */}
      {documentos.length > 0 && (
        <div className={`${styles.docList} ${recentlyAdded ? styles.highlight : ""}`}>
          <p><strong>📋 Documentos adicionados:</strong></p>
          <ul>
            {documentos.map((d, i) => (
              <li
                key={i}
                className={`${styles.docItemRow} ${d.animating ? styles.docItemEnter : ""}`}
              >
                <span className={styles.docItem}>
                  {i + 1}. {d.tipo}
                </span>
                <span className={styles.docMeta}>({d.origem || "—"})</span>
                <button
                  onClick={() => handleRemove(i)}
                  className={styles.btnRemove}
                  type="button"
                  title="Remover documento"
                >
                  ❌
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </form>
  );
}
