// pages/AnaliseRiscos/index.tsx - Página principal de Análise de Riscos
import { useEffect } from 'react';
import { useRiscosStore } from '../../store/riscosStore';
import UploadOuSelecionaPOP from '../../components/AnaliseRiscos/UploadOuSelecionaPOP';
import ChatRiscos from '../../components/AnaliseRiscos/ChatRiscos';
import RelatorioRiscos from '../../components/AnaliseRiscos/RelatorioRiscos';
import styles from './index.module.css';

export default function AnaliseRiscosPage() {
  const { currentStep, reset } = useRiscosStore();

  // Limpar ao desmontar (opcional)
  useEffect(() => {
    return () => {
      // Não resetar automaticamente para permitir voltar à página
      // reset();
    };
  }, []);

  return (
    <div className={styles.page}>
      {/* Step: Upload */}
      {currentStep === 'upload' && <UploadOuSelecionaPOP />}

      {/* Step: Chat (Perguntas) */}
      {currentStep === 'chat' && <ChatRiscos />}

      {/* Step: Relatório */}
      {currentStep === 'relatorio' && <RelatorioRiscos />}

      {/* Step: PDF (mesmo que relatório) */}
      {currentStep === 'pdf' && <RelatorioRiscos />}
    </div>
  );
}
