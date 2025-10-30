import React, { useState } from 'react';
import './InterfaceRagPerguntaAtividade.css';

interface HierarquiaHerdada {
    macroprocesso: string;
    processo: string;
    subprocesso: string;
}

interface Props {
    mensagem: string;
    hierarquiaHerdada: HierarquiaHerdada;
    onEnviar: (descricao: string) => void;
}

const InterfaceRagPerguntaAtividade: React.FC<Props> = ({
    mensagem,
    hierarquiaHerdada,
    onEnviar
}) => {
    const [descricao, setDescricao] = useState('');
    const [enviando, setEnviando] = useState(false);

    const handleEnviar = async () => {
        if (!descricao.trim()) {
            alert('Por favor, descreva sua atividade antes de enviar');
            return;
        }

        setEnviando(true);
        try {
            await onEnviar(descricao.trim());
        } finally {
            setEnviando(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleEnviar();
        }
    };

    const caracteresRestantes = 500 - descricao.length;
    const podEnviar = descricao.trim().length >= 10 && !enviando;

    return (
        <div className="rag-pergunta-container">
            <div className="rag-header">
                <span className="rag-icone">🤖</span>
                <div className="rag-titulo-grupo">
                    <h3 className="rag-titulo">Helena está te ouvindo</h3>
                    <p className="rag-subtitulo">Criando nova atividade...</p>
                </div>
            </div>

            {/* Hierarquia Herdada */}
            <div className="hierarquia-herdada">
                <h4 className="hierarquia-titulo">📍 Sua atividade será criada em:</h4>
                <div className="hierarquia-path">
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

            {/* Mensagem da Helena */}
            <div className="rag-mensagem-helena">
                <div className="helena-avatar">
                    <span>💬</span>
                </div>
                <div className="helena-balao">
                    <p>{mensagem}</p>
                </div>
            </div>

            {/* Campo de Descrição */}
            <div className="rag-input-grupo">
                <label className="rag-label">
                    Descreva sua atividade
                    <span className="rag-obrigatorio">*</span>
                </label>
                <textarea
                    className="rag-textarea"
                    value={descricao}
                    onChange={(e) => setDescricao(e.target.value.slice(0, 500))}
                    onKeyDown={handleKeyPress}
                    placeholder="Exemplo: Eu analiso documentos de aposentadoria por tempo de contribuição, verifico se os períodos contributivos estão corretos e faço o cálculo do tempo total..."
                    maxLength={500}
                    rows={6}
                    disabled={enviando}
                />
                <div className="rag-input-rodape">
                    <span className={`caracteres-contador ${caracteresRestantes < 50 ? 'alerta' : ''}`}>
                        {caracteresRestantes} caracteres restantes
                    </span>
                    <span className="rag-dica">
                        💡 Dica: Use Ctrl+Enter para enviar
                    </span>
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

            {/* Botão de Enviar */}
            <div className="rag-acoes">
                <button
                    className="btn-enviar-rag"
                    onClick={handleEnviar}
                    disabled={!podEnviar}
                >
                    {enviando ? (
                        <>
                            <span className="btn-spinner">⏳</span>
                            Processando...
                        </>
                    ) : (
                        <>
                            <span className="btn-icone">🚀</span>
                            Enviar para Helena
                        </>
                    )}
                </button>
            </div>

            {/* Rodapé */}
            <div className="rag-rodape">
                <div className="rodape-info">
                    <span className="rodape-icone">🔒</span>
                    <span className="rodape-texto">
                        Helena irá sugerir um nome apropriado para sua atividade com base na sua descrição
                    </span>
                </div>
            </div>
        </div>
    );
};

export default InterfaceRagPerguntaAtividade;
