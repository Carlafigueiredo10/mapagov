import { useState, useRef, DragEvent } from 'react';
import axios from 'axios';
import './FluxogramaUpload.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface FluxogramaUploadProps {
  onPdfAnalyzed: (popInfo: any) => void;
}

export default function FluxogramaUpload({ onPdfAnalyzed }: FluxogramaUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<string>('Aguardando upload...');
  const [progress, setProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (selectedFile: File) => {
    if (selectedFile.type !== 'application/pdf') {
      alert('Por favor, selecione um arquivo PDF válido.');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) { // 10MB
      alert('Arquivo muito grande. Tamanho máximo: 10MB');
      return;
    }

    setFile(selectedFile);
    setStatus('Pronto para análise');
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setStatus('Analisando PDF...');
    setProgress(50);

    const formData = new FormData();
    formData.append('pdf_file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/fluxograma-from-pdf/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setStatus('✅ Analisado com sucesso!');
        setProgress(100);
        onPdfAnalyzed(response.data.pop_info);

        setTimeout(() => {
          setProgress(0);
        }, 2000);
      } else {
        setStatus('❌ Erro na análise');
        setProgress(0);
      }
    } catch (error) {
      console.error('Erro ao fazer upload:', error);
      setStatus('❌ Erro de conexão');
      setProgress(0);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fluxograma-upload">
      <div
        className={`upload-area ${isDragging ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <div className="upload-icon">📄</div>
        <h3>Clique ou arraste o PDF aqui</h3>
        <p>Arquivo PDF do POP (máx. 10MB)</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleInputChange}
          style={{ display: 'none' }}
        />
      </div>

      {file && (
        <div className="file-info">
          <strong>Arquivo:</strong> {file.name}<br />
          <strong>Tamanho:</strong> {(file.size / 1024).toFixed(2)} KB<br />
          <strong>Status:</strong> {status}
        </div>
      )}

      <button
        className="upload-btn"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? 'Analisando...' : 'Analisar PDF'}
      </button>

      {progress > 0 && (
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
}
