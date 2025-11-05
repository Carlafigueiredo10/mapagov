/**
 * Página de Diagnóstico Guiado
 * Questionário de 5 perguntas para recomendar modelo ideal
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import perguntasData from '../data/perguntasDiagnostico.json';
import type { PerguntaDiagnostico } from '../types/planejamento';
import './DiagnosticoGuiado.css';

const PERGUNTAS_DIAGNOSTICO: PerguntaDiagnostico[] = perguntasData;

export const DiagnosticoGuiado: React.FC = () => {
  const navigate = useNavigate();
  const [perguntaAtual, setPerguntaAtual] = useState(0);
  const [respostasDiagnostico, setRespostasDiagnostico] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const responderPergunta = (opcaoSelecionada: string) => {
    const pergunta = PERGUNTAS_DIAGNOSTICO[perguntaAtual];

    // Salva resposta
    const novasRespostas = {
      ...respostasDiagnostico,
      [pergunta.id]: opcaoSelecionada
    };
    setRespostasDiagnostico(novasRespostas);

    // Se ainda há perguntas, avança
    if (perguntaAtual < PERGUNTAS_DIAGNOSTICO.length - 1) {
      setPerguntaAtual(perguntaAtual + 1);
    } else {
      // Finaliza diagnóstico e calcula recomendação
      finalizarDiagnostico(novasRespostas);
    }
  };

  const finalizarDiagnostico = (respostas: Record<string, string>) => {
    setLoading(true);

    // Lógica de recomendação baseada nas respostas
    const modeloRecomendado = calcularRecomendacao(respostas);

    // Redireciona para a página do modelo recomendado após 1 segundo
    setTimeout(() => {
      navigate(modeloRecomendado);
    }, 1000);
  };

  const calcularRecomendacao = (respostas: Record<string, string>): string => {
    // Lógica simplificada de recomendação
    const maturidade = respostas['maturidade'];
    const tempo = respostas['tempo'];
    const complexidade = respostas['complexidade'];

    // Se é iniciante e quer algo rápido
    if (maturidade === 'iniciante' && tempo === 'curto') {
      return '/planejamento-estrategico/modelos/5w2h';
    }

    // Se quer diagnóstico situacional
    if (complexidade === 'diagnostico') {
      return '/planejamento-estrategico/modelos/swot';
    }

    // Se tem urgência mas alguma experiência
    if (tempo === 'curto' && maturidade !== 'iniciante') {
      return '/planejamento-estrategico/modelos/okr';
    }

    // Se tem tempo e quer algo completo
    if (tempo === 'longo' && complexidade === 'alta') {
      return '/planejamento-estrategico/modelos/bsc';
    }

    // Se quer pensar em cenários futuros
    if (complexidade === 'incerteza') {
      return '/planejamento-estrategico/modelos/cenarios';
    }

    // Se quer algo formal e tradicional
    if (maturidade === 'avancado') {
      return '/planejamento-estrategico/modelos/tradicional';
    }

    // Padrão: OKR (recomendado pelo MGI)
    return '/planejamento-estrategico/modelos/okr';
  };

  const pergunta = PERGUNTAS_DIAGNOSTICO[perguntaAtual];
  const percentual = Math.round(((perguntaAtual + 1) / PERGUNTAS_DIAGNOSTICO.length) * 100);

  return (
    <div className="diagnostico-guiado-page">
      <div className="diagnostico-container">
        {/* Header */}
        <div className="diagnostico-header">
          <div className="diagnostico-icone">🩺</div>
          <h1>Diagnóstico Guiado</h1>
          <p className="diagnostico-progresso-texto">
            Pergunta {perguntaAtual + 1} de {PERGUNTAS_DIAGNOSTICO.length}
          </p>
        </div>

        {/* Card da Pergunta */}
        <Card variant="glass" className="diagnostico-card">
          <h2 className="diagnostico-pergunta">{pergunta.texto}</h2>

          <div className="diagnostico-opcoes">
            {pergunta.opcoes.map((opcao) => (
              <Button
                key={opcao.valor}
                variant="outline"
                onClick={() => responderPergunta(opcao.valor)}
                disabled={loading}
                size="lg"
                className="diagnostico-opcao-btn"
              >
                {opcao.texto}
              </Button>
            ))}
          </div>
        </Card>

        {loading && (
          <div className="diagnostico-loading">
            ⏳ Analisando suas respostas e recomendando o melhor modelo...
          </div>
        )}

        {/* Barra de Progresso */}
        <div className="diagnostico-progresso-barra-container">
          <div className="diagnostico-progresso-barra">
            <div
              className="diagnostico-progresso-fill"
              style={{ width: `${percentual}%` }}
            />
          </div>
          <p className="diagnostico-progresso-percentual">{percentual}% completo</p>
        </div>

        {/* Botão Cancelar */}
        <div className="diagnostico-footer">
          <Button
            variant="outline"
            onClick={() => navigate('/planejamento-estrategico')}
            size="md"
            disabled={loading}
          >
            ← Cancelar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DiagnosticoGuiado;
