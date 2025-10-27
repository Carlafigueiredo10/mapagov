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
    background_especial
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
    <div className={`transicao-epica-container ${background_especial ? 'background-especial' : ''}`}>
      {mostrar_progresso && progresso_texto && (
        <div className="progresso-badge">
          ✅ {progresso_texto}
        </div>
      )}

      <div className="botoes-transicao">
        <button
          className={`botao-transicao ${botao_principal.classe} ${botao_principal.animacao}`}
          style={{
            backgroundColor: botao_principal.cor,
            fontSize: botao_principal.tamanho === 'grande' ? '1.3rem' : '1rem'
          }}
          onClick={handleClickPrincipal}
        >
          {botao_principal.texto}
        </button>

        {botao_secundario && (
          <button
            className={`botao-transicao ${botao_secundario.classe}`}
            onClick={handleClickSecundario}
            style={{
              marginTop: botao_secundario.posicao === 'abaixo' ? '1rem' : '0'
            }}
          >
            {botao_secundario.texto}
          </button>
        )}
      </div>
    </div>
  );
};

export default InterfaceTransicaoEpica;