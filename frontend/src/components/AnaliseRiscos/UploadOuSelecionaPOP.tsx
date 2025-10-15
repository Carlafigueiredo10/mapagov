// UploadOuSelecionaPOP.tsx - Upload de PDF ou Seleção de POP existente
import { useState } from 'react';
import { useRiscosStore } from '../../store/riscosStore';
import { uploadPDFPOP } from '../../services/riscosApi';
import styles from './UploadOuSelecionaPOP.module.css';

export default function UploadOuSelecionaPOP() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const setPOPFromUpload = useRiscosStore((state) => state.setPOPFromUpload);

  const handleFileSelect = async (file: File) => {
    if (!file.type.includes('pdf')) {
      setError('Por favor, selecione apenas arquivos PDF');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const result = await uploadPDFPOP(file);

      if (result.success) {
        setPOPFromUpload(result.text, result.pop_info);
      } else {
        setError(result.error || 'Erro ao processar PDF');
      }
    } catch (err) {
      console.error('Erro no upload:', err);
      setError('Erro ao fazer upload do arquivo');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>⚠️ Análise de Riscos - POP</h1>
        <p>Faça upload do POP em PDF para iniciar a análise inteligente de riscos</p>
      </div>

      <div className={styles.uploadSection}>
        <div
          className={`${styles.uploadZone} ${dragActive ? styles.dragActive : ''} ${
            isUploading ? styles.uploading : ''
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !isUploading && document.getElementById('file-input')?.click()}
        >
          {isUploading ? (
            <>
              <div className={styles.spinner} />
              <p>Extraindo texto do PDF...</p>
              <small>Analisando estrutura do POP</small>
            </>
          ) : (
            <>
              <div className={styles.uploadIcon}>📄</div>
              <h3>Clique aqui ou arraste o arquivo PDF</h3>
              <p>Apenas arquivos PDF do Procedimento Operacional Padrão</p>
              <button className={styles.btnPrimary}>
                Selecionar Arquivo
              </button>
            </>
          )}

          <input
            id="file-input"
            type="file"
            accept=".pdf"
            style={{ display: 'none' }}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFileSelect(file);
            }}
            disabled={isUploading}
          />
        </div>

        {error && (
          <div className={styles.error}>
            <span>❌</span>
            <p>{error}</p>
          </div>
        )}
      </div>

      <div className={styles.infoBox}>
        <h4>📋 O que será analisado:</h4>
        <ul>
          <li>✓ Estrutura completa do POP</li>
          <li>✓ Sistemas utilizados</li>
          <li>✓ Normativos aplicáveis</li>
          <li>✓ Operadores e responsáveis</li>
          <li>✓ Etapas e fluxos do processo</li>
        </ul>
      </div>

      <div className={styles.helenaNote}>
        <span className={styles.helenaIcon}>🤖</span>
        <p>
          <strong>Helena</strong> irá te fazer 20 perguntas contextualizadas para complementar
          a análise do POP. Em seguida, a IA analisará os riscos usando os referenciais
          COSO ERM, ISO 31000 e Modelo das Três Linhas.
        </p>
      </div>
    </div>
  );
}
