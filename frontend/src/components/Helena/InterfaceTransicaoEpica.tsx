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

interface BotaoSecundario {
  texto: string;
  classe: string;
  posicao: string;
  valor_enviar: string;
}

interface InterfaceTransicaoEpicaProps {
  dados: {
    botao_principal: BotaoPrincipal;
    botao_secundario?: BotaoSecundario;
    mostrar_progresso?: boolean;
    progresso_texto?: string;
    background_especial?: boolean;
  };
  onEnviar: (valor: string) => void;
}

const InterfaceTransicaoEpica: React.FC<InterfaceTransicaoEpicaProps> = ({ dados, onEnviar }) => {
  const {
    botao_principal,
    botao_secundario,
    mostrar_progresso,
    progresso_texto,
  } = dados;

  const handleClickPrincipal = () => {
    onEnviar(botao_principal.valor_enviar);
  };

  const handleClickSecundario = () => {
    if (botao_secundario) {
      onEnviar(botao_secundario.valor_enviar);
    }
  };

  return (
    <div className="transicao-epica-container">
      {mostrar_progresso && progresso_texto && (
        <div className="progresso-badge">
          ✅ {progresso_texto}
        </div>
      )}

      <div className="botoes-transicao-dupla">
        {botao_secundario && (
          <button
            className="btn-transicao btn-transicao-secundario"
            onClick={handleClickSecundario}
          >
            {botao_secundario.texto}
          </button>
        )}

        <button
          className="btn-transicao btn-transicao-principal"
          onClick={handleClickPrincipal}
        >
          {botao_principal.texto}
        </button>
      </div>
    </div>
  );
};

export default InterfaceTransicaoEpica;
