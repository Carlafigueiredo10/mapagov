import React from 'react';
import './InterfaceSugestaoAtividade.css';

interface AtividadeSugerida {
    macroprocesso: string;
    processo: string;
    subprocesso: string;
    atividade: string;
}

interface Props {
    atividade: AtividadeSugerida;
    cap: string;
    origem: 'match_exato' | 'match_fuzzy' | 'semantic' | 'rag_nova_atividade';
    score: number;
    podeEditar: boolean;
    onConcordar: () => void;
    onSelecionarManual: () => void;
}

const InterfaceSugestaoAtividade: React.FC<Props> = ({
    atividade,
    cap,
    origem,
    score,
    podeEditar,
    onConcordar,
    onSelecionarManual
}) => {
    const obterTituloOrigem = () => {
        switch (origem) {
            case 'match_exato':
                return 'Encontrei uma correspondência exata!';
            case 'match_fuzzy':
                return 'Encontrei uma correspondência similar!';
            case 'semantic':
                return 'Encontrei uma atividade parecida com o que você me disse que faz na sua rotina:';
            case 'rag_nova_atividade':
                return 'Pelo que você me falou, achei que a melhor definição pra sua atividade é:';
            default:
                return 'Atividade encontrada';
        }
    };

    const obterIconeOrigem = () => {
        switch (origem) {
            case 'match_exato':
                return '✓';
            case 'match_fuzzy':
                return '≈';
            case 'semantic':
                return null; // Usará imagem
            case 'rag_nova_atividade':
                return null; // Usará imagem
            default:
                return '•';
        }
    };

    return (
        <div className="sugestao-atividade-container">
            <div className="sugestao-header">
                {(origem === 'semantic' || origem === 'rag_nova_atividade') ? (
                    <img
                        src="/helena_mapeamento.png"
                        alt="Helena"
                        className="sugestao-icone-img"
                        style={{ width: '32px', height: '32px', borderRadius: '50%' }}
                    />
                ) : (
                    <span className="sugestao-icone">{obterIconeOrigem()}</span>
                )}
                <h3 className="sugestao-titulo">{obterTituloOrigem()}</h3>
                {origem === 'match_exato' && (
                    <span className="badge-match-exato">100% Match</span>
                )}
                {origem === 'semantic' && (
                    <span className="badge-semantic">{Math.round(score * 100)}% Similar</span>
                )}
                {origem === 'rag_nova_atividade' && (
                    <span className="badge-semantic">Nova Atividade</span>
                )}
            </div>

            <div className="sugestao-conteudo">
                <div className="campo-info">
                    <label>CAP (Código na Arquitetura do Processo)</label>
                    <div className="valor-cap">{cap}</div>
                </div>

                <div className="campo-info">
                    <label>Macroprocesso</label>
                    <div className="valor">{atividade.macroprocesso}</div>
                </div>

                <div className="campo-info">
                    <label>Processo</label>
                    <div className="valor">{atividade.processo}</div>
                </div>

                <div className="campo-info">
                    <label>Subprocesso</label>
                    <div className="valor">{atividade.subprocesso}</div>
                </div>

                <div className="campo-info destaque">
                    <label>Atividade</label>
                    <div className="valor-atividade">{atividade.atividade}</div>
                </div>
            </div>

            {!podeEditar && (
                <div className="aviso-nao-editavel">
                    <span className="icone-lock">🔒</span>
                    <span>Esta atividade está no catálogo oficial e não pode ser editada</span>
                </div>
            )}

            <div className="sugestao-acoes">
                <button
                    className="btn-concordar"
                    onClick={onConcordar}
                >
                    <span className="btn-icone">✓</span>
                    Você acertou, Helena!
                </button>

                <button
                    className="btn-selecionar-manual"
                    onClick={onSelecionarManual}
                >
                    <span className="btn-icone">🧭</span>
                    {origem === 'rag_nova_atividade'
                        ? 'Não é essa minha atividade, vou digitar o que faço'
                        : 'Não é essa minha atividade, vou selecionar manualmente'
                    }
                </button>
            </div>

            <div className="sugestao-rodape">
                <span className="texto-ajuda">
                    Você pode concordar com esta classificação ou explorar outras opções manualmente
                </span>
            </div>
        </div>
    );
};

export default InterfaceSugestaoAtividade;
