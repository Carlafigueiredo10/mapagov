import React from 'react';
import { useChatStore } from '../../store/chatStore';
import './InterfaceSugestaoEntregaEsperada.css';

interface Props {
    sugestao: string;
    onConcordar: () => void;
    onEditarManual: () => void;
}

const InterfaceSugestaoEntregaEsperada: React.FC<Props> = ({
    sugestao,
    onConcordar,
    onEditarManual
}) => {
    const isProcessing = useChatStore((s) => s.isProcessing);

    return (
        <div className="sugestao-entrega-container">
            <div className="sugestao-entrega-conteudo">
                <div className="campo-sugestao">
                    <label>Minha sugestão:</label>
                    <div className="valor-sugestao">{sugestao}</div>
                </div>

                <p className="texto-pergunta">
                    O que você acha? Pode concordar ou sugerir outra entrega.
                </p>
            </div>

            <div className="sugestao-entrega-acoes">
                <button
                    className="btn-concordar-entrega"
                    onClick={onConcordar}
                    disabled={isProcessing}
                >
                    <span className="btn-icone">✅</span>
                    Concordo com a sugestão
                </button>

                <button
                    className="btn-editar-manual"
                    onClick={onEditarManual}
                    disabled={isProcessing}
                >
                    <span className="btn-icone">✏️</span>
                    Quero editar manualmente
                </button>
            </div>
        </div>
    );
};

export default InterfaceSugestaoEntregaEsperada;
