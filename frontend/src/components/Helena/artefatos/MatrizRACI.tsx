/**
 * Matriz de Entregas e Responsáveis (RACI)
 * Artefato do Domínio 2 - Escopo e Valor
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface EntregaRACI {
  id: string;
  entrega: string;
  responsavel: string;
  aprovador: string;
  consultado: string;
  informado: string;
}

export const MatrizRACI: React.FC = () => {
  const [entregas, setEntregas] = useState<EntregaRACI[]>([
    {
      id: '1',
      entrega: 'Plano de capacitação',
      responsavel: 'Coordenação de Projetos',
      aprovador: 'Diretor',
      consultado: 'CGRIS',
      informado: 'Equipe técnica'
    },
    {
      id: '2',
      entrega: 'Relatório final',
      responsavel: 'Analista',
      aprovador: 'Coordenador',
      consultado: 'Comitê',
      informado: 'Gabinete'
    }
  ]);

  const handleChange = (id: string, campo: keyof Omit<EntregaRACI, 'id'>, valor: string) => {
    setEntregas(entregas.map(e =>
      e.id === id ? { ...e, [campo]: valor } : e
    ));
  };

  const adicionarEntrega = () => {
    const novaEntrega: EntregaRACI = {
      id: Date.now().toString(),
      entrega: '',
      responsavel: '',
      aprovador: '',
      consultado: '',
      informado: ''
    };
    setEntregas([...entregas, novaEntrega]);
  };

  const removerEntrega = (id: string) => {
    setEntregas(entregas.filter(e => e.id !== id));
  };

  const handleExportar = () => {
    let texto = 'MATRIZ DE ENTREGAS E RESPONSÁVEIS (RACI)\n';
    texto += '=' .repeat(50) + '\n\n';
    texto += 'Entrega\t|\tResponsável (R)\t|\tAprovador (A)\t|\tConsultado (C)\t|\tInformado (I)\n';
    texto += '-'.repeat(100) + '\n';

    entregas.forEach(e => {
      texto += `${e.entrega}\t|\t${e.responsavel}\t|\t${e.aprovador}\t|\t${e.consultado}\t|\t${e.informado}\n`;
    });

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'matriz-raci.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>👥 Matriz de Entregas e Responsáveis (RACI)</h2>
        <p className="artefato-descricao">
          Garante clareza sobre quem <strong>faz</strong>, <strong>aprova</strong>, <strong>consulta</strong> e <strong>é informado</strong> sobre cada entrega.
        </p>
        <div className="raci-legenda">
          <span><strong>R</strong> = Responsável (quem executa)</span>
          <span><strong>A</strong> = Aprovador (quem valida)</span>
          <span><strong>C</strong> = Consultado (quem opina)</span>
          <span><strong>I</strong> = Informado (quem precisa saber)</span>
        </div>
      </div>

      <div className="matriz-raci-container">
        <table className="matriz-raci-table">
          <thead>
            <tr>
              <th>Entrega</th>
              <th>Responsável (R)</th>
              <th>Aprovador (A)</th>
              <th>Consultado (C)</th>
              <th>Informado (I)</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {entregas.map((entrega) => (
              <tr key={entrega.id}>
                <td>
                  <input
                    type="text"
                    value={entrega.entrega}
                    onChange={(e) => handleChange(entrega.id, 'entrega', e.target.value)}
                    placeholder="Nome da entrega"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={entrega.responsavel}
                    onChange={(e) => handleChange(entrega.id, 'responsavel', e.target.value)}
                    placeholder="Quem executa"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={entrega.aprovador}
                    onChange={(e) => handleChange(entrega.id, 'aprovador', e.target.value)}
                    placeholder="Quem valida"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={entrega.consultado}
                    onChange={(e) => handleChange(entrega.id, 'consultado', e.target.value)}
                    placeholder="Quem opina"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={entrega.informado}
                    onChange={(e) => handleChange(entrega.id, 'informado', e.target.value)}
                    placeholder="Quem precisa saber"
                  />
                </td>
                <td>
                  <button
                    className="btn-remover"
                    onClick={() => removerEntrega(entrega.id)}
                    title="Remover entrega"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <button className="btn-adicionar" onClick={adicionarEntrega}>
          ➕ Adicionar Entrega
        </button>
      </div>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Matriz RACI
        </button>
        <button className="btn-secundario" onClick={() => window.history.back()}>
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default MatrizRACI;
