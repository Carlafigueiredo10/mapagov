/**
 * Mapa de Papéis e Responsabilidades (RACI Expandido)
 * Artefato do Domínio 3 - Equipe e Responsabilidades
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface AtividadeRaci {
  id: string;
  atividade: string;
  executa: string;
  apoia: string;
  aprova: string;
  acompanha: string;
}

export const MapaPapeisRaci: React.FC = () => {
  const [atividades, setAtividades] = useState<AtividadeRaci[]>([
    {
      id: '1',
      atividade: 'Definir escopo e cronograma',
      executa: 'Coordenação',
      apoia: 'Equipe técnica',
      aprova: 'Comitê',
      acompanha: 'Direção'
    },
    {
      id: '2',
      atividade: 'Elaborar relatório final',
      executa: 'Analista',
      apoia: 'Comunicação',
      aprova: 'Coordenação',
      acompanha: 'Gabinete'
    }
  ]);

  const handleChange = (id: string, campo: keyof Omit<AtividadeRaci, 'id'>, valor: string) => {
    setAtividades(atividades.map(a =>
      a.id === id ? { ...a, [campo]: valor } : a
    ));
  };

  const adicionarAtividade = () => {
    const novaAtividade: AtividadeRaci = {
      id: Date.now().toString(),
      atividade: '',
      executa: '',
      apoia: '',
      aprova: '',
      acompanha: ''
    };
    setAtividades([...atividades, novaAtividade]);
  };

  const removerAtividade = (id: string) => {
    setAtividades(atividades.filter(a => a.id !== id));
  };

  const handleExportar = () => {
    let texto = 'MAPA DE PAPÉIS E RESPONSABILIDADES (RACI EXPANDIDO)\n';
    texto += '='.repeat(70) + '\n\n';
    texto += 'Legenda:\n';
    texto += '  Executa (R) - Quem realiza a atividade\n';
    texto += '  Apoia (S) - Quem fornece suporte\n';
    texto += '  Aprova (A) - Quem valida e autoriza\n';
    texto += '  Acompanha (I) - Quem precisa ser informado\n\n';
    texto += '-'.repeat(70) + '\n';
    texto += 'Atividade\t|\tExecuta\t|\tApoia\t|\tAprova\t|\tAcompanha\n';
    texto += '-'.repeat(70) + '\n';

    atividades.forEach(a => {
      texto += `${a.atividade}\t|\t${a.executa}\t|\t${a.apoia}\t|\t${a.aprova}\t|\t${a.acompanha}\n`;
    });

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'mapa-papeis-raci.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>👥 Mapa de Papéis e Responsabilidades (RACI Expandido)</h2>
        <p className="artefato-descricao">
          Organiza de forma clara quem <strong>executa</strong>, quem <strong>apoia</strong>,
          quem <strong>aprova</strong> e quem <strong>acompanha</strong> cada atividade do projeto.
        </p>
        <div className="raci-legenda">
          <span><strong>Executa (R)</strong> = Responsável pela execução</span>
          <span><strong>Apoia (S)</strong> = Fornece suporte</span>
          <span><strong>Aprova (A)</strong> = Valida e autoriza</span>
          <span><strong>Acompanha (I)</strong> = Precisa ser informado</span>
        </div>
      </div>

      <div className="matriz-raci-container">
        <table className="matriz-raci-table">
          <thead>
            <tr>
              <th>Atividade</th>
              <th>Executa (R)</th>
              <th>Apoia (S)</th>
              <th>Aprova (A)</th>
              <th>Acompanha (I)</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {atividades.map((atividade) => (
              <tr key={atividade.id}>
                <td>
                  <input
                    type="text"
                    value={atividade.atividade}
                    onChange={(e) => handleChange(atividade.id, 'atividade', e.target.value)}
                    placeholder="Nome da atividade"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={atividade.executa}
                    onChange={(e) => handleChange(atividade.id, 'executa', e.target.value)}
                    placeholder="Quem executa"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={atividade.apoia}
                    onChange={(e) => handleChange(atividade.id, 'apoia', e.target.value)}
                    placeholder="Quem apoia"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={atividade.aprova}
                    onChange={(e) => handleChange(atividade.id, 'aprova', e.target.value)}
                    placeholder="Quem aprova"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={atividade.acompanha}
                    onChange={(e) => handleChange(atividade.id, 'acompanha', e.target.value)}
                    placeholder="Quem acompanha"
                  />
                </td>
                <td>
                  <button
                    className="btn-remover"
                    onClick={() => removerAtividade(atividade.id)}
                    title="Remover atividade"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <button className="btn-adicionar" onClick={adicionarAtividade}>
          ➕ Adicionar Atividade
        </button>
      </div>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Mapa RACI
        </button>
        <button className="btn-secundario" onClick={() => window.history.back()}>
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default MapaPapeisRaci;
