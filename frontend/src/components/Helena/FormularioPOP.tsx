import React, { useState, useEffect, useMemo } from 'react';
import { useChatStore } from '../../store/chatStore';
import { FileText, CheckCircle, AlertCircle, Download, Eye } from 'lucide-react';
import type { Etapa, Cenario } from '../../types/pop.types';
import './FormularioPOP.css';

const FormularioPOP: React.FC = () => {
  const { dadosPOP, modoRevisao, updateDadosPOP, resetChat } = useChatStore();
  
  // Estado local para campos editáveis
  const [formData, setFormData] = useState(dadosPOP);
  const [validacoes, setValidacoes] = useState<Record<string, 'valido' | 'invalido' | ''>>({});
  const [camposPreenchidos, setCamposPreenchidos] = useState(0);
  const [ultimoCampoPreenchido, setUltimoCampoPreenchido] = useState<string | null>(null);

  // Lista de todos os campos do formulário
  const todosCampos = useMemo(() => [
    'area', 'codigo_processo', 'macroprocesso', 'processo_especifico',
    'subprocesso', 'nome_processo', 'entrega_esperada', 'dispositivos_normativos',
    'sistemas', 'operadores', 'etapas', 'documentos_utilizados', 'pontos_atencao',
    'fluxos_entrada', 'fluxos_saida'
  ], []);

  // Sync com store quando dados mudam
  useEffect(() => {
    setFormData(dadosPOP);
  }, [dadosPOP]);

  // Auto-scroll quando campo é preenchido
  useEffect(() => {
    // Detectar qual campo foi preenchido (comparar formData anterior com atual)
    const camposAtuais = Object.keys(dadosPOP);

    for (const campo of camposAtuais) {
      const valorNovo = dadosPOP[campo as keyof typeof dadosPOP];
      const valorAntigo = formData[campo as keyof typeof formData];

      // Verificar se o campo foi preenchido AGORA
      const foiPreenchidoAgora =
        valorNovo &&
        (valorAntigo === undefined || valorAntigo === null || valorAntigo === '' ||
         (Array.isArray(valorAntigo) && valorAntigo.length === 0)) &&
        (typeof valorNovo === 'string' && valorNovo.trim().length > 0 ||
         Array.isArray(valorNovo) && valorNovo.length > 0 ||
         typeof valorNovo === 'object' && Object.keys(valorNovo).length > 0);

      if (foiPreenchidoAgora && campo !== ultimoCampoPreenchido) {
        setUltimoCampoPreenchido(campo);

        // Fazer scroll suave até o campo recém-preenchido
        setTimeout(() => {
          const elemento = document.getElementById(campo);
          if (elemento) {
            elemento.scrollIntoView({
              behavior: 'smooth',
              block: 'center',
              inline: 'nearest'
            });

            // Animação de destaque (pulso)
            elemento.classList.add('campo-destacado');
            setTimeout(() => {
              elemento.classList.remove('campo-destacado');
            }, 2000);
          }
        }, 300); // Delay para garantir que o DOM foi atualizado

        break; // Processar apenas o primeiro campo mudado
      }
    }
  }, [dadosPOP, formData, ultimoCampoPreenchido]);

  // Calcular campos preenchidos
  useEffect(() => {
    const preenchidos = todosCampos.filter(campo => {
      const valor = formData[campo as keyof typeof formData];
      if (Array.isArray(valor)) {
        return valor.length > 0;
      }
      if (typeof valor === 'object' && valor !== null) {
        return Object.keys(valor).length > 0;
      }
      return valor && String(valor).trim().length > 3;
    });
    setCamposPreenchidos(preenchidos.length);
  }, [formData, todosCampos]);

  const handleInputChange = (campo: string, valor: string) => {
    const novosDados = { ...formData, [campo]: valor };
    setFormData(novosDados);
    
    // Atualizar store se em modo revisão
    if (modoRevisao) {
      updateDadosPOP(novosDados);
    }
    
    // Validação simples
    if (valor.trim().length > 3) {
      setValidacoes(prev => ({ ...prev, [campo]: 'valido' }));
    } else if (valor.trim().length > 0) {
      setValidacoes(prev => ({ ...prev, [campo]: 'invalido' }));
    } else {
      setValidacoes(prev => ({ ...prev, [campo]: '' }));
    }
  };

  const renderCampo = (
    id: string,
    label: string,
    tipo: 'input' | 'textarea' = 'input',
    readonly: boolean = false
  ) => {
    const valor = formData[id as keyof typeof formData];
    let valorString = '';

    if (Array.isArray(valor)) {
      valorString = valor.join(', ');
    } else if (typeof valor === 'object' && valor !== null) {
      // Verifica se é um objeto com codigo e nome
      if ('codigo' in valor && 'nome' in valor) {
        valorString = `${valor.codigo} - ${valor.nome}`;
      } else {
        // Se for outro tipo de objeto, tenta converter para JSON
        valorString = JSON.stringify(valor);
      }
    } else if (valor !== null && valor !== undefined) {
      valorString = String(valor);
    }

    const validacao = validacoes[id];

    return (
      <div className="form-group" key={id}>
        <label htmlFor={id}>{label}</label>
        {tipo === 'textarea' ? (
          <textarea
            id={id}
            value={valorString}
            onChange={(e) => handleInputChange(id, e.target.value)}
            readOnly={readonly}
            className={`form-field ${validacao} ${valorString ? 'preenchido' : ''}`}
            placeholder={readonly ? 'Será preenchido pela conversa...' : 'Digite aqui...'}
          />
        ) : (
          <input
            type="text"
            id={id}
            value={valorString}
            onChange={(e) => handleInputChange(id, e.target.value)}
            readOnly={readonly}
            className={`form-field ${validacao} ${valorString ? 'preenchido' : ''}`}
            placeholder={readonly ? 'Será preenchido pela conversa...' : 'Digite aqui...'}
          />
        )}
        <div className="validacao-feedback">
          {validacao === 'valido' && <CheckCircle className="icon-valido" size={16} />}
          {validacao === 'invalido' && <AlertCircle className="icon-invalido" size={16} />}
        </div>
      </div>
    );
  };

  const porcentagemPreenchimento = (camposPreenchidos / todosCampos.length) * 100;

  return (
    <div className={`form-section ${modoRevisao ? 'modo-revisao' : ''}`}>
      {/* Header */}
      <div className="form-header">
        <div className="fields-indicator">
          {camposPreenchidos}/{todosCampos.length} campos
        </div>
        <h2>
          {modoRevisao ? '✓ Formulário do POP - Revisão Final' : 'Formulário do POP'}
        </h2>
        
        {/* Barra de progresso do preenchimento */}
        <div className="form-progress-container">
          <div 
            className="form-progress-bar" 
            style={{ width: `${porcentagemPreenchimento}%` }}
          />
        </div>
        <div className="form-progress-text">
          {Math.round(porcentagemPreenchimento)}% preenchido
        </div>
      </div>

      {/* Content */}
      <div className="form-content">
        {/* Identificação */}
        <div className="form-section-header">
          <h3>📋 Identificação do Processo</h3>
        </div>

        {renderCampo('codigo_processo', 'Código na Arquitetura de Processos', 'input', true)}
        {renderCampo('area', 'Área DECIPEX', 'input', true)}
        {renderCampo('macroprocesso', 'Macroprocesso', 'input', true)}
        {renderCampo('processo_especifico', 'Processo', 'input', true)}
        {renderCampo('subprocesso', 'Subprocesso', 'input', true)}
        {renderCampo('nome_processo', 'Atividade', 'input', true)}

        {/* Entrega */}
        <div className="form-section-header">
          <h3>1. Entrega Esperada</h3>
        </div>

        {renderCampo('entrega_esperada', 'Entrega Esperada da Atividade', 'textarea')}

        {/* Sistemas */}
        <div className="form-section-header">
          <h3>2. Sistemas Utilizados</h3>
        </div>

        {renderCampo('sistemas', 'Sistemas Utilizados / Acessos Necessários', 'textarea', true)}

        {/* Normativos */}
        <div className="form-section-header">
          <h3>3. Dispositivos Normativos</h3>
        </div>

        {renderCampo('dispositivos_normativos', 'Dispositivos Normativos Aplicáveis', 'textarea')}

        {/* Operadores */}
        <div className="form-section-header">
          <h3>4. Operadores</h3>
        </div>

        {renderCampo('operadores', 'Operadores da Atividade', 'textarea')}

        {/* Entrada do Processo */}
        <div className="form-section-header">
          <h3>5. Entrada do Processo</h3>
        </div>

        {renderCampo('fluxos_entrada', 'De quais áreas recebe insumos', 'textarea', true)}

        {/* Etapas */}
        <div className="form-section-header">
          <h3>6. Tarefas/Etapas</h3>
        </div>

        <div className="form-group">
          <label>Etapas do Processo</label>
          <div className="etapas-display">
            {Array.isArray(formData.etapas) && formData.etapas.length > 0 ? (
              formData.etapas.map((etapa: any, index: number) => {
                const isCondicional = etapa.tipo === 'condicional';
                return (
                  <div key={index} className={`etapa-item ${isCondicional ? 'etapa-condicional' : ''}`}>
                    <div className="etapa-numero">
                      📌 Etapa {etapa.numero || index + 1}
                      {isCondicional && <span className="etapa-badge-condicional">🔀 Condicional</span>}
                    </div>
                    <div className="etapa-descricao">
                      <strong>
                        {typeof etapa === 'string'
                          ? etapa
                          : etapa.descricao || JSON.stringify(etapa)}
                      </strong>

                      {/* Operador */}
                      {(etapa.operador_nome || etapa.operador) && (
                        <div className="etapa-operador">
                          👤 {etapa.operador_nome || etapa.operador}
                        </div>
                      )}

                      {/* Sistemas */}
                      {etapa.sistemas && Array.isArray(etapa.sistemas) && etapa.sistemas.length > 0 && (
                        <div className="etapa-sistemas">
                          🖥️ Sistemas: {etapa.sistemas.join(', ')}
                        </div>
                      )}

                      {/* Docs requeridos */}
                      {etapa.docs_requeridos && Array.isArray(etapa.docs_requeridos) && etapa.docs_requeridos.length > 0 && (
                        <div className="etapa-docs">
                          📥 Docs requeridos: {etapa.docs_requeridos.join(', ')}
                        </div>
                      )}

                      {/* Docs gerados */}
                      {etapa.docs_gerados && Array.isArray(etapa.docs_gerados) && etapa.docs_gerados.length > 0 && (
                        <div className="etapa-docs">
                          📤 Docs gerados: {etapa.docs_gerados.join(', ')}
                        </div>
                      )}

                      {/* Tempo estimado */}
                      {etapa.tempo_estimado && (
                        <div className="etapa-tempo">
                          ⏱️ Tempo estimado: {etapa.tempo_estimado}
                        </div>
                      )}

                      {/* Detalhes (etapas lineares) */}
                      {etapa.detalhes && Array.isArray(etapa.detalhes) && etapa.detalhes.length > 0 && (
                        <div className="etapa-detalhes">
                          {etapa.detalhes.map((detalhe: string, idx: number) => (
                            <div key={idx} className="detalhe-item">• {detalhe}</div>
                          ))}
                        </div>
                      )}

                      {/* Cenários (etapas condicionais) */}
                      {isCondicional && etapa.antes_decisao && (
                        <div className="etapa-antes-decisao">
                          ⚡ Antes da decisão: {
                            typeof etapa.antes_decisao === 'object'
                              ? etapa.antes_decisao.descricao
                              : etapa.antes_decisao
                          }
                        </div>
                      )}

                      {isCondicional && etapa.cenarios && Array.isArray(etapa.cenarios) && (
                        <div className="cenarios-lista">
                          <div className="condicional-titulo">🔀 Cenários:</div>
                          {etapa.cenarios.map((cenario: Cenario, idx: number) => (
                            <div key={idx} className="cenario-item">
                              <strong>Cenário {cenario.numero || idx + 1}:</strong>{' '}
                              {cenario.descricao}
                              {cenario.subetapas && Array.isArray(cenario.subetapas) && cenario.subetapas.length > 0 && (
                                <div className="subetapas-lista">
                                  {cenario.subetapas.map((sub, subIdx: number) => (
                                    <div key={subIdx} className="subetapa-item">
                                      {sub.numero} {sub.descricao}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="etapas-placeholder">
                As etapas serão listadas aqui conforme a conversa...
              </div>
            )}
          </div>
        </div>

        {/* Saída do Processo */}
        <div className="form-section-header">
          <h3>7. Saída do Processo</h3>
        </div>

        {renderCampo('fluxos_saida', 'Para quais áreas entrega resultados', 'textarea', true)}

        {/* Documentos */}
        <div className="form-section-header">
          <h3>8. Documentos</h3>
        </div>

        <div className="form-group">
          <label>Documentos, Formulários e Modelos Utilizados</label>
          <div className="documentos-display">
            {Array.isArray(formData.documentos_utilizados) && formData.documentos_utilizados.length > 0 ? (
              formData.documentos_utilizados.map((doc: any, index: number) => (
                <div key={index} className="documento-item-form">
                  <div className="documento-header">
                    <span className="documento-tipo">
                      📄 {typeof doc.tipo_documento === 'string' ? doc.tipo_documento : 'Documento'}
                    </span>
                    <span className={`documento-badge ${doc.obrigatorio ? 'obrigatorio' : 'opcional'}`}>
                      {doc.obrigatorio ? 'Obrigatório' : 'Opcional'}
                    </span>
                    <span className={`documento-badge ${doc.tipo_uso === 'Gerado' ? 'gerado' : 'utilizado'}`}>
                      {typeof doc.tipo_uso === 'string' ? doc.tipo_uso : 'Utilizado'}
                    </span>
                  </div>
                  <div className="documento-descricao-form">
                    {typeof doc.descricao === 'string'
                      ? doc.descricao
                      : typeof doc === 'string'
                      ? doc
                      : JSON.stringify(doc)}
                  </div>
                  {doc.sistema && typeof doc.sistema === 'string' && (
                    <div className="documento-sistema">🖥️ Sistema: {doc.sistema}</div>
                  )}
                </div>
              ))
            ) : (
              <div className="documentos-placeholder">
                Os documentos serão listados aqui conforme a conversa...
              </div>
            )}
          </div>
        </div>

        {/* Pontos de Atenção */}
        <div className="form-section-header">
          <h3>9. Pontos de Atenção</h3>
        </div>

        {renderCampo('pontos_atencao', 'Pontos Gerais de Atenção na Atividade', 'textarea')}
      </div>

      {/* Actions */}
      <div className="form-actions">
        <button
          type="button"
          className="btn-form limpar"
          onClick={() => {
            if (confirm('Tem certeza que deseja iniciar um novo mapeamento? Isso irá limpar o formulário e a conversa atual.')) {
              // Limpar estado local
              setFormData({});
              setValidacoes({});

              // Reset completo do chat store
              resetChat();

              // Opcional: Recarregar a página para garantir estado limpo
              window.location.reload();
            }
          }}
        >
          <FileText size={16} />
          Limpar
        </button>
        
        <button 
          type="button" 
          className="btn-form ver-preview"
          disabled={camposPreenchidos < 5}
        >
          <Eye size={16} />
          Ver Preview
        </button>
        
        <button 
          type="button" 
          className={`btn-form gerar-pdf ${modoRevisao ? 'ativo' : ''}`}
          disabled={camposPreenchidos < 8}
        >
          <Download size={16} />
          Gerar PDF
        </button>
      </div>
    </div>
  );
};

export default FormularioPOP;