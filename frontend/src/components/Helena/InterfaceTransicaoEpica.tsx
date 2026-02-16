import React from 'react';
import './InterfaceTransicaoEpica.css';

interface BotaoPrincipal {
  texto: string;
  classe: string;
  tamanho: string;
  cor: string;
  animacao: string;
  valor_enviar: string;
}

interface InterfaceTransicaoEpicaProps {
  dados: {
    botao_principal: BotaoPrincipal;
    mostrar_progresso?: boolean;
    progresso_texto?: string;
  };
  onEnviar: (valor: string) => void;
}

const InterfaceTransicaoEpica: React.FC<InterfaceTransicaoEpicaProps> = ({ dados, onEnviar }) => {
  const { botao_principal, mostrar_progresso, progresso_texto } = dados;

  return (
    <div className="transicao-epica-container">
      {mostrar_progresso && progresso_texto && (
        <div className="progresso-badge">
          ✅ {progresso_texto}
        </div>
      )}

      <div className="botoes-transicao-dupla">
        <button
          className="btn-transicao btn-transicao-principal"
          onClick={() => onEnviar(botao_principal.valor_enviar)}
        >
          {botao_principal.texto}
        </button>
      </div>
    </div>
  );
};

export default InterfaceTransicaoEpica;
