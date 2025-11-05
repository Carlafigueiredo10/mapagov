import React, { useState } from 'react';
import './InterfaceSelecaoManualHierarquica.css';

interface Atividade {
    atividade: string;
    cap: string;
}

interface Hierarquia {
    [macroprocesso: string]: {
        [processo: string]: {
            [subprocesso: string]: Atividade[];
        };
    };
}

interface Props {
    hierarquia: Hierarquia;
    mensagem: string;
    onConfirmar: (selecao: {
        macroprocesso: string;
        processo: string;
        subprocesso: string;
        atividade: string;
        cap: string;
    }) => void;
    onNaoEncontrei: (selecao: {
        macroprocesso: string;
        processo: string;
        subprocesso: string;
    }) => void;
}

const InterfaceSelecaoManualHierarquica: React.FC<Props> = ({
    hierarquia,
    mensagem,
    onConfirmar,
    onNaoEncontrei
}) => {
    const [macroSelecionado, setMacroSelecionado] = useState<string>('');
    const [processoSelecionado, setProcessoSelecionado] = useState<string>('');
    const [subprocessoSelecionado, setSubprocessoSelecionado] = useState<string>('');
    const [atividadeSelecionada, setAtividadeSelecionada] = useState<string>('');

    const macroprocessos = Object.keys(hierarquia);
    const processos = macroSelecionado ? Object.keys(hierarquia[macroSelecionado]) : [];
    const subprocessos = macroSelecionado && processoSelecionado
        ? Object.keys(hierarquia[macroSelecionado][processoSelecionado])
        : [];
    const atividades = macroSelecionado && processoSelecionado && subprocessoSelecionado
        ? hierarquia[macroSelecionado][processoSelecionado][subprocessoSelecionado]
        : [];

    const handleMacroChange = (macro: string) => {
        setMacroSelecionado(macro);
        setProcessoSelecionado('');
        setSubprocessoSelecionado('');
        setAtividadeSelecionada('');
    };

    const handleProcessoChange = (processo: string) => {
        setProcessoSelecionado(processo);
        setSubprocessoSelecionado('');
        setAtividadeSelecionada('');
    };

    const handleSubprocessoChange = (subprocesso: string) => {
        setSubprocessoSelecionado(subprocesso);
        setAtividadeSelecionada('');
    };

    const handleAtividadeChange = (atividade: string) => {
        setAtividadeSelecionada(atividade);
    };

    const handleConfirmar = () => {
        if (!atividadeSelecionada) {
            alert('Por favor, selecione uma atividade antes de confirmar');
            return;
        }

        const atividadeObj = atividades.find(a => a.atividade === atividadeSelecionada);
        if (!atividadeObj) return;

        onConfirmar({
            macroprocesso: macroSelecionado,
            processo: processoSelecionado,
            subprocesso: subprocessoSelecionado,
            atividade: atividadeSelecionada,
            cap: atividadeObj.cap
        });
    };

    const handleNaoEncontrei = () => {
        if (!subprocessoSelecionado) {
            alert('Por favor, selecione pelo menos até o nível de Subprocesso antes de prosseguir');
            return;
        }

        onNaoEncontrei({
            macroprocesso: macroSelecionado,
            processo: processoSelecionado,
            subprocesso: subprocessoSelecionado
        });
    };

    const podeConfirmar = !!atividadeSelecionada;
    const podeNaoEncontrei = !!subprocessoSelecionado;

    return (
        <div className="selecao-manual-container">
            <div className="selecao-header">
                <span className="selecao-icone">🧭</span>
                <h3 className="selecao-titulo">Seleção Manual de Atividade</h3>
            </div>

            <div className="selecao-mensagem">
                <p>{mensagem}</p>
            </div>

            <div className="selecao-niveis">
                {/* NÍVEL 1: Macroprocesso */}
                <div className="nivel-container">
                    <label className="nivel-label">
                        <span className="nivel-numero">1</span>
                        Macroprocesso
                    </label>
                    <select
                        className="nivel-select"
                        value={macroSelecionado}
                        onChange={(e) => handleMacroChange(e.target.value)}
                    >
                        <option value="">Selecione um macroprocesso...</option>
                        {macroprocessos.map(macro => (
                            <option key={macro} value={macro}>{macro}</option>
                        ))}
                    </select>
                </div>

                {/* NÍVEL 2: Processo */}
                {macroSelecionado && (
                    <div className="nivel-container nivel-ativo">
                        <label className="nivel-label">
                            <span className="nivel-numero">2</span>
                            Processo
                        </label>
                        <select
                            className="nivel-select"
                            value={processoSelecionado}
                            onChange={(e) => handleProcessoChange(e.target.value)}
                        >
                            <option value="">Selecione um processo...</option>
                            {processos.map(processo => (
                                <option key={processo} value={processo}>{processo}</option>
                            ))}
                        </select>
                    </div>
                )}

                {/* NÍVEL 3: Subprocesso */}
                {processoSelecionado && (
                    <div className="nivel-container nivel-ativo">
                        <label className="nivel-label">
                            <span className="nivel-numero">3</span>
                            Subprocesso
                        </label>
                        <select
                            className="nivel-select"
                            value={subprocessoSelecionado}
                            onChange={(e) => handleSubprocessoChange(e.target.value)}
                        >
                            <option value="">Selecione um subprocesso...</option>
                            {subprocessos.map(subprocesso => (
                                <option key={subprocesso} value={subprocesso}>{subprocesso}</option>
                            ))}
                        </select>
                    </div>
                )}

                {/* NÍVEL 4: Atividade */}
                {subprocessoSelecionado && (
                    <div className="nivel-container nivel-ativo nivel-final">
                        <label className="nivel-label">
                            <span className="nivel-numero">4</span>
                            Atividade
                        </label>

                        {/* Alerta com Sirene Pulsante */}
                        <div className="alerta-nao-encontrei">
                            <div className="sirene-pulsante">🚨</div>
                            <p className="alerta-texto">
                                Se não encontrar <strong>exatamente</strong> sua atividade, clique em
                                <span className="destaque-botao"> ➕ Não encontrei minha atividade</span> e me conta o que faz.
                            </p>
                        </div>

                        <div className="atividades-lista">
                            {atividades.map((ativ, index) => (
                                <div
                                    key={index}
                                    className={`atividade-item ${atividadeSelecionada === ativ.atividade ? 'selecionada' : ''}`}
                                    onClick={() => handleAtividadeChange(ativ.atividade)}
                                >
                                    <div className="atividade-radio">
                                        {atividadeSelecionada === ativ.atividade && <span className="radio-check">●</span>}
                                    </div>
                                    <div className="atividade-info">
                                        <div className="atividade-nome">{ativ.atividade}</div>
                                        <div className="atividade-cap">CAP: {ativ.cap}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Resumo da Seleção */}
            {subprocessoSelecionado && (
                <div className="selecao-resumo">
                    <h4>Hierarquia Selecionada:</h4>
                    <div className="resumo-path">
                        <span className="path-item">{macroSelecionado}</span>
                        <span className="path-separator">›</span>
                        <span className="path-item">{processoSelecionado}</span>
                        <span className="path-separator">›</span>
                        <span className="path-item">{subprocessoSelecionado}</span>
                        {atividadeSelecionada && (
                            <>
                                <span className="path-separator">›</span>
                                <span className="path-item path-atividade">{atividadeSelecionada}</span>
                            </>
                        )}
                    </div>
                </div>
            )}

            {/* Botões de Ação */}
            <div className="selecao-acoes">
                <button
                    className="btn-confirmar"
                    onClick={handleConfirmar}
                    disabled={!podeConfirmar}
                >
                    <span className="btn-icone">✓</span>
                    Confirmar Seleção
                </button>

                <button
                    className="btn-nao-encontrei"
                    onClick={handleNaoEncontrei}
                    disabled={!podeNaoEncontrei}
                >
                    <span className="btn-icone">➕</span>
                    Não encontrei minha atividade
                </button>
            </div>

            <div className="selecao-rodape">
                <span className="texto-ajuda">
                    Navegue pela estrutura hierárquica ou clique em "Não encontrei" para criar uma nova atividade
                </span>
            </div>
        </div>
    );
};

export default InterfaceSelecaoManualHierarquica;
