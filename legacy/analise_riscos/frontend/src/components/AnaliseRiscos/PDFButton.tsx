// PDFButton.tsx - Botão para gerar PDF do relatório
import { useState } from 'react';
import { gerarPDFRiscos, downloadPDF } from '../../services/riscosApi';
import type { RelatorioRiscos } from './types';
import styles from './PDFButton.module.css';

interface PDFButtonProps {
  relatorio: RelatorioRiscos;
  variant?: 'default' | 'large';
}

export default function PDFButton({ relatorio, variant = 'default' }: PDFButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGeneratePDF = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      // TODO: Implementar endpoint backend para gerar PDF
      // Por enquanto, gerar PDF no client-side ou mostrar mensagem

      // Simulação (remover quando backend estiver pronto)
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Gerar PDF client-side como fallback
      generateClientSidePDF();

    } catch (err) {
      console.error('Erro ao gerar PDF:', err);
      setError('Erro ao gerar PDF. Tente novamente.');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateClientSidePDF = () => {
    // Gerar texto formatado do relatório
    let pdfText = `
═══════════════════════════════════════════════════
  RELATÓRIO DE ANÁLISE DE RISCOS - MapaGov Helena
═══════════════════════════════════════════════════

POP: ${relatorio.cabecalho.pop}
Código: ${relatorio.cabecalho.codigo}
Responsável: ${relatorio.cabecalho.responsavel}
Data da Análise: ${relatorio.cabecalho.data_analise}

───────────────────────────────────────────────────
  MATRIZ DE RISCOS
───────────────────────────────────────────────────

🔴 Riscos Críticos: ${relatorio.matriz_riscos.criticos}
🟠 Riscos Altos: ${relatorio.matriz_riscos.altos}
🟡 Riscos Moderados: ${relatorio.matriz_riscos.moderados}
🟢 Riscos Baixos: ${relatorio.matriz_riscos.baixos}

Total de Riscos Identificados: ${relatorio.riscos.length}

───────────────────────────────────────────────────
  SUMÁRIO EXECUTIVO
───────────────────────────────────────────────────

MAIORES RISCOS:
${relatorio.sumario_executivo.maiores_riscos.map((r, i) => `${i + 1}. ${r}`).join('\n')}

ÁREAS CRÍTICAS:
${relatorio.sumario_executivo.areas_criticas.map((a, i) => `• ${a}`).join('\n')}

AÇÕES URGENTES:
${relatorio.sumario_executivo.acoes_urgentes.map((a, i) => `• ${a}`).join('\n')}

SÍNTESE GERENCIAL:
${relatorio.sumario_executivo.sintese_gerencial}

───────────────────────────────────────────────────
  RISCOS IDENTIFICADOS
───────────────────────────────────────────────────

${relatorio.riscos.map((risco, index) => `
═══ RISCO ${index + 1} - ${risco.severidade.toUpperCase()} ═══

Título: ${risco.titulo}
Categoria: ${risco.categoria}

Descrição:
${risco.descricao}

Análise:
• Probabilidade: ${risco.probabilidade}
• Impacto: ${risco.impacto}
• Tipo: ${risco.tipo_risco}
${risco.normativo_relacionado !== 'Não aplicável' ? `• Normativo: ${risco.normativo_relacionado}` : ''}

💡 Tratamento Recomendado:
${risco.tratamento_recomendado}

✓ Controles Existentes:
${risco.controles_existentes.map(c => `  • ${c}`).join('\n')}

📊 Indicadores de Monitoramento:
${risco.indicadores_monitoramento.map(i => `  • ${i}`).join('\n')}

`).join('\n')}

───────────────────────────────────────────────────
  PLANO DE TRATAMENTO
───────────────────────────────────────────────────

MITIGAÇÃO IMEDIATA:
${relatorio.plano_tratamento.mitigacao_imediata.map((m, i) => `${i + 1}. ${m}`).join('\n')}

MONITORAMENTO:
${relatorio.plano_tratamento.monitoramento.map((m, i) => `• ${m}`).join('\n')}

LACUNAS DE CONTROLE:
${relatorio.plano_tratamento.lacunas_controle.map((l, i) => `• ${l}`).join('\n')}

───────────────────────────────────────────────────
  CONCLUSÕES E RECOMENDAÇÕES
───────────────────────────────────────────────────

${relatorio.conclusoes_recomendacoes}

═══════════════════════════════════════════════════
Relatório gerado por Helena GRC - MapaGov
Baseado em COSO ERM (2017), ISO 31000 (2018),
Modelo das Três Linhas (IIA, 2020) e Referencial
Básico de Governança do TCU
═══════════════════════════════════════════════════
`;

    // Download como TXT
    const blob = new Blob([pdfText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Relatorio_Riscos_${relatorio.cabecalho.codigo}_${new Date().toISOString().split('T')[0]}.txt`;
    link.click();
    URL.revokeObjectURL(url);

    // Notificar sucesso
    alert('✅ Relatório exportado com sucesso!');
  };

  const buttonClass = variant === 'large'
    ? styles.btnLarge
    : styles.btn;

  return (
    <div className={styles.container}>
      <button
        className={buttonClass}
        onClick={handleGeneratePDF}
        disabled={isGenerating}
      >
        {isGenerating ? (
          <>
            <span className={styles.spinner} />
            Gerando PDF...
          </>
        ) : (
          <>
            📥 Gerar PDF
          </>
        )}
      </button>

      {error && (
        <div className={styles.error}>
          {error}
        </div>
      )}
    </div>
  );
}
