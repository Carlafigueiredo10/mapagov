import React from 'react';
import './InterfaceRagPerguntaAtividade.css';

interface HierarquiaHerdada {
    area?: string;
    macroprocesso: string;
    processo: string;
    subprocesso: string;
}

interface Props {
    hierarquiaHerdada: HierarquiaHerdada;
    onEnviar: (descricao: string) => void;
}

const InterfaceRagPerguntaAtividade: React.FC<Props> = ({
    hierarquiaHerdada
}) => {
    console.log('🎨 InterfaceRagPerguntaAtividade render (modo informativo)');

    return (
        <div className="rag-pergunta-container">
            <div className="rag-header">
                <img src="/helena_mapeamento.png" alt="Helena" className="rag-icone-img" />
                <div className="rag-titulo-grupo">
                    <p className="rag-mensagem-principal">Estou te ouvindo, me conta o que você faz e vamos definir a atividade certa</p>
                </div>
            </div>

            {/* Hierarquia Herdada */}
            <div className="hierarquia-herdada">
                <h4 className="hierarquia-titulo">📍 Sua atividade será criada em:</h4>
                <div className="hierarquia-path">
                    {hierarquiaHerdada.area && (
                        <>
                            <div className="hierarquia-item">
                                <span className="hierarquia-label">Área</span>
                                <span className="hierarquia-valor">{hierarquiaHerdada.area}</span>
                            </div>
                            <span className="hierarquia-seta">↓</span>
                        </>
                    )}
                    <div className="hierarquia-item">
                        <span className="hierarquia-label">Macroprocesso</span>
                        <span className="hierarquia-valor">{hierarquiaHerdada.macroprocesso}</span>
                    </div>
                    <span className="hierarquia-seta">↓</span>
                    <div className="hierarquia-item">
                        <span className="hierarquia-label">Processo</span>
                        <span className="hierarquia-valor">{hierarquiaHerdada.processo}</span>
                    </div>
                    <span className="hierarquia-seta">↓</span>
                    <div className="hierarquia-item">
                        <span className="hierarquia-label">Subprocesso</span>
                        <span className="hierarquia-valor">{hierarquiaHerdada.subprocesso}</span>
                    </div>
                </div>
            </div>

            {/* Exemplos */}
            <div className="rag-exemplos">
                <h5 className="exemplos-titulo">Exemplos de boas descrições:</h5>
                <div className="exemplos-lista">
                    <div className="exemplo-item">
                        <span className="exemplo-icone">✓</span>
                        <span>"Eu reviso processos de pensão por morte, verifico documentação e análise de direito"</span>
                    </div>
                    <div className="exemplo-item">
                        <span className="exemplo-icone">✓</span>
                        <span>"Faço atendimento de servidores sobre dúvidas previdenciárias por telefone"</span>
                    </div>
                    <div className="exemplo-item">
                        <span className="exemplo-icone">✓</span>
                        <span>"Cadastro novos beneficiários no sistema SIAPE após aprovação"</span>
                    </div>
                </div>
            </div>

            {/* Instrução para digitar no chat */}
            <div className="rag-rodape">
                <div className="rodape-info">
                    <span className="rodape-icone">💬</span>
                    <span className="rodape-texto">
                        Digite sua resposta na barra de chat abaixo
                    </span>
                </div>
            </div>
        </div>
    );
};

export default InterfaceRagPerguntaAtividade;
