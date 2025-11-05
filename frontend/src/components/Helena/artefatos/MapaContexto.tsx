import React, { useState } from 'react';
import './Artefatos.css';

type TipoFator = 'interno' | 'externo';
type ImpactoPotencial = 'positivo' | 'negativo' | 'neutro';
type NivelImpacto = 'baixo' | 'medio' | 'alto';

interface FatorContexto {
  id: string;
  fator: string;
  tipo: TipoFator;
  impacto: ImpactoPotencial;
  nivelImpacto: NivelImpacto;
  acaoMonitoramento: string;
}

export const MapaContexto: React.FC = () => {
  const [fatores, setFatores] = useState<FatorContexto[]>([
    {
      id: '1',
      fator: 'Mudança de gestão',
      tipo: 'externo',
      impacto: 'negativo',
      nivelImpacto: 'alto',
      acaoMonitoramento: 'Alinhar com nova direção'
    },
    {
      id: '2',
      fator: 'Corte orçamentário',
      tipo: 'externo',
      impacto: 'negativo',
      nivelImpacto: 'alto',
      acaoMonitoramento: 'Planejar contingência'
    },
    {
      id: '3',
      fator: 'Novas tecnologias disponíveis',
      tipo: 'externo',
      impacto: 'positivo',
      nivelImpacto: 'medio',
      acaoMonitoramento: 'Integrar ferramentas'
    }
  ]);

  const adicionarFator = () => {
    const novoFator: FatorContexto = {
      id: Date.now().toString(),
      fator: '',
      tipo: 'externo',
      impacto: 'neutro',
      nivelImpacto: 'medio',
      acaoMonitoramento: ''
    };
    setFatores([...fatores, novoFator]);
  };

  const removerFator = (id: string) => {
    setFatores(fatores.filter(f => f.id !== id));
  };

  const atualizarFator = (id: string, campo: keyof FatorContexto, valor: any) => {
    setFatores(fatores.map(f => f.id === id ? { ...f, [campo]: valor } : f));
  };

  const getImpactoColor = (impacto: ImpactoPotencial): string => {
    const colors = { positivo: '#198754', negativo: '#dc3545', neutro: '#6c757d' };
    return colors[impacto];
  };

  const getNivelColor = (nivel: NivelImpacto): string => {
    const colors = { baixo: '#6c757d', medio: '#ffc107', alto: '#dc3545' };
    return colors[nivel];
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  MAPA DE CONTEXTO E FATORES EXTERNOS\n';
    conteudo += '  Domínio 6 - Incerteza e Contexto\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    fatores.forEach((fator, index) => {
      conteudo += `${index + 1}. ${fator.fator || '(não identificado)'}\n`;
      conteudo += `   Tipo: ${fator.tipo === 'interno' ? 'Interno' : 'Externo'}\n`;
      conteudo += `   Impacto: ${fator.impacto} (Nível: ${fator.nivelImpacto})\n`;
      conteudo += `   Ação: ${fator.acaoMonitoramento || '—'}\n\n`;
    });

    conteudo += `Total de fatores: ${fatores.length}\n`;
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'mapa_contexto.txt';
    link.click();
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>🌍 Mapa de Contexto e Fatores Externos</h2>
          <p className="artefato-descricao">
            Identificar variáveis do ambiente que influenciam o projeto.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarFator}>
          ➕ Adicionar Fator
        </button>
      </div>

      <div className="tabela-stakeholders">
        <table>
          <thead>
            <tr>
              <th style={{ width: '30%' }}>Fator</th>
              <th style={{ width: '12%' }}>Tipo</th>
              <th style={{ width: '15%' }}>Impacto</th>
              <th style={{ width: '12%' }}>Nível</th>
              <th style={{ width: '28%' }}>Ação de Monitoramento</th>
              <th style={{ width: '3%' }}></th>
            </tr>
          </thead>
          <tbody>
            {fatores.map((fator) => (
              <tr key={fator.id}>
                <td>
                  <input
                    type="text"
                    value={fator.fator}
                    onChange={(e) => atualizarFator(fator.id, 'fator', e.target.value)}
                    placeholder="Descrição do fator"
                    className="input-inline"
                  />
                </td>
                <td>
                  <select
                    value={fator.tipo}
                    onChange={(e) => atualizarFator(fator.id, 'tipo', e.target.value)}
                    className="select-inline"
                  >
                    <option value="interno">Interno</option>
                    <option value="externo">Externo</option>
                  </select>
                </td>
                <td>
                  <select
                    value={fator.impacto}
                    onChange={(e) => atualizarFator(fator.id, 'impacto', e.target.value)}
                    className="select-inline"
                    style={{ backgroundColor: getImpactoColor(fator.impacto), color: 'white' }}
                  >
                    <option value="positivo">✅ Positivo</option>
                    <option value="negativo">⚠️ Negativo</option>
                    <option value="neutro">➖ Neutro</option>
                  </select>
                </td>
                <td>
                  <select
                    value={fator.nivelImpacto}
                    onChange={(e) => atualizarFator(fator.id, 'nivelImpacto', e.target.value)}
                    className="select-inline"
                    style={{ backgroundColor: getNivelColor(fator.nivelImpacto), color: 'white' }}
                  >
                    <option value="baixo">Baixo</option>
                    <option value="medio">Médio</option>
                    <option value="alto">Alto</option>
                  </select>
                </td>
                <td>
                  <input
                    type="text"
                    value={fator.acaoMonitoramento}
                    onChange={(e) => atualizarFator(fator.id, 'acaoMonitoramento', e.target.value)}
                    placeholder="Ação de monitoramento"
                    className="input-inline"
                  />
                </td>
                <td>
                  <button
                    className="btn-remover-table"
                    onClick={() => removerFator(fator.id)}
                    title="Remover"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {fatores.length === 0 && (
        <div className="empty-state">
          <p>Nenhum fator cadastrado. Clique em "Adicionar Fator" para começar.</p>
        </div>
      )}
    </div>
  );
};

export default MapaContexto;
