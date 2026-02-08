/**
 * PlanejamentoLanding - Página inicial institucional de Planejamento Estratégico
 *
 * Extraído de HelenaPEModerna.renderInicial() para padronização.
 * Mantém estilo original (inline styles com gradiente) por ser visualmente
 * distinto das demais landings (Riscos, POP).
 */
import React, { CSSProperties } from 'react';
import Button from '../ui/Button';

interface PlanejamentoLandingProps {
  onNavigate: (path: string) => void;
  onAbrirDashboardAreas: () => void;
  onAbrirDashboardDiretor: () => void;
  estatisticas?: {
    total_projetos: number;
    total_pedidos: number;
  };
}

const PlanejamentoLanding: React.FC<PlanejamentoLandingProps> = ({
  onNavigate,
  onAbrirDashboardAreas,
  onAbrirDashboardDiretor,
  estatisticas,
}) => {
  const cardStyle: CSSProperties = {
    background: 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(8px)',
    borderRadius: '16px',
    padding: '28px 32px',
    border: '1px solid rgba(27, 79, 114, 0.1)',
    boxShadow: '0 4px 16px rgba(27, 79, 114, 0.06)'
  };

  const sectionTitle: CSSProperties = {
    fontSize: '22px',
    fontWeight: 700,
    color: '#1B4F72',
    marginBottom: '20px',
    lineHeight: 1.3
  };

  const subTitle: CSSProperties = {
    fontSize: '18px',
    fontWeight: 700,
    color: '#1B4F72',
    marginBottom: '10px',
    lineHeight: 1.3
  };

  const linkBtnStyle: CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 20px',
    background: 'rgba(255, 255, 255, 0.95)',
    border: '1px solid rgba(27, 79, 114, 0.12)',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontSize: '15px',
    fontWeight: 600,
    color: '#1B4F72',
    width: '100%',
    textAlign: 'left' as const
  };

  return (
    <div style={{ maxWidth: '1100px', width: '100%', zIndex: 1 }}>
      {/* HEADER */}
      <h1 style={{ fontSize: '36px', fontWeight: 800, color: '#1B4F72', marginBottom: '24px', lineHeight: 1.2, textAlign: 'center' }}>
        Planejamento Estratégico
      </h1>
      <div style={{ ...cardStyle, marginBottom: '24px', background: '#ffffff' }}>
        <p style={{ fontSize: '16px', lineHeight: 1.8, color: '#34495E', marginBottom: '12px' }}>
          Crie, organize e acompanhe o planejamento estratégico institucional ao longo de todo o ciclo oficial (PPA, PEI, PDTI e instrumentos equivalentes).
        </p>
        <p style={{ fontSize: '15px', lineHeight: 1.7, color: '#4a5568', margin: 0 }}>
          Este ambiente pode ser utilizado de duas formas: como <strong>sistema completo</strong>, para criar, registrar e acompanhar projetos estratégicos; ou como <strong>fonte de ferramentas</strong>, para apoiar um planejamento já existente no seu órgão.
        </p>
      </div>

      {/* HELENA — APOIO */}
      <div style={{
        ...cardStyle,
        marginBottom: '40px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '32px',
        background: '#ffffff',
        borderLeft: '4px solid #1B4F72'
      }}>
        <img
          src="/helena_plano.png"
          alt="Helena"
          style={{
            width: '160px',
            height: 'auto',
            flexShrink: 0
          }}
        />
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#1B4F72', marginBottom: '12px' }}>
            Helena — Apoio ao Planejamento Estratégico
          </h2>
          <p style={{ fontSize: '15px', lineHeight: 1.7, color: '#2C3E50', marginBottom: '12px' }}>
            Helena é o ecossistema de apoio ao Planejamento Estratégico. Ela auxilia na compreensão dos conceitos, na escolha de modelos e no uso adequado das ferramentas ao longo do processo.
          </p>
          <p style={{ fontSize: '14px', lineHeight: 1.6, color: '#4a5568', marginBottom: '8px' }}>
            A Helena pode estar disponível como:
          </p>
          <ul style={{ margin: '0 0 12px', paddingLeft: '20px', listStyleType: 'disc', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <li style={{ fontSize: '14px', color: '#4a5568', lineHeight: 1.5 }}>apoio contextual nas páginas e formulários;</li>
            <li style={{ fontSize: '14px', color: '#4a5568', lineHeight: 1.5 }}>chat para esclarecimento de dúvidas sobre planejamento estratégico;</li>
            <li style={{ fontSize: '14px', color: '#4a5568', lineHeight: 1.5 }}>suporte durante o uso dos modelos e ferramentas.</li>
          </ul>
          <p style={{ fontSize: '13px', color: '#6b7280', lineHeight: 1.5, margin: 0 }}>
            As decisões, registros e validações permanecem sob responsabilidade do usuário e das instâncias institucionais competentes.
          </p>
        </div>
      </div>

      {/* O QUE VOCÊ PODE FAZER AQUI */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={sectionTitle}>O que você pode fazer aqui</h2>
        <p style={{ fontSize: '15px', color: '#4a5568', marginBottom: '24px' }}>
          Escolha como deseja avançar de acordo com sua necessidade atual.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
          {/* Iniciar */}
          <div style={cardStyle}>
            <h3 style={subTitle}>Iniciar ou estruturar um planejamento</h3>
            <p style={{ fontSize: '14px', lineHeight: 1.7, color: '#4a5568', marginBottom: '12px' }}>
              Utilize modelos orientados e ferramentas estruturadas para iniciar um novo ciclo de planejamento estratégico ou estruturar projetos estratégicos.
            </p>
            <p style={{ fontSize: '13px', fontWeight: 600, color: '#1B4F72', marginBottom: '6px' }}>Indicado para:</p>
            <ul style={{ margin: '0 0 20px', paddingLeft: '18px', listStyleType: 'disc', display: 'flex', flexDirection: 'column', gap: '3px' }}>
              <li style={{ fontSize: '13px', color: '#4a5568' }}>início de ciclos oficiais;</li>
              <li style={{ fontSize: '13px', color: '#4a5568' }}>criação de novos projetos estratégicos;</li>
              <li style={{ fontSize: '13px', color: '#4a5568' }}>estruturação inicial de objetivos, iniciativas e indicadores.</li>
            </ul>
            <Button
              variant="primary"
              onClick={() => onNavigate('/planejamento-estrategico/modelos')}
              size="md"
              style={{
                background: 'linear-gradient(135deg, #1B4F72 0%, #2874A6 100%)',
                color: '#fff',
                border: 'none',
                fontWeight: 600,
                width: '100%'
              }}
            >
              Iniciar planejamento estratégico
            </Button>
          </div>

          {/* Acompanhar */}
          <div style={cardStyle}>
            <h3 style={subTitle}>Acompanhar planejamentos e projetos</h3>
            <p style={{ fontSize: '14px', lineHeight: 1.7, color: '#4a5568', marginBottom: '12px' }}>
              Acesse painéis para acompanhar o andamento dos projetos estratégicos, demandas da Direção e prazos institucionais.
            </p>
            <p style={{ fontSize: '13px', fontWeight: 600, color: '#1B4F72', marginBottom: '6px' }}>Indicado para:</p>
            <ul style={{ margin: '0 0 20px', paddingLeft: '18px', listStyleType: 'disc', display: 'flex', flexDirection: 'column', gap: '3px' }}>
              <li style={{ fontSize: '13px', color: '#4a5568' }}>acompanhamento contínuo;</li>
              <li style={{ fontSize: '13px', color: '#4a5568' }}>monitoramento de execução;</li>
              <li style={{ fontSize: '13px', color: '#4a5568' }}>consolidação de informações para governança.</li>
            </ul>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={onAbrirDashboardAreas}
                style={linkBtnStyle}
                onMouseEnter={e => { e.currentTarget.style.background = 'rgba(27, 79, 114, 0.05)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)'; }}
              >
                Dashboard das Áreas <span>→</span>
              </button>
              <button
                onClick={onAbrirDashboardDiretor}
                style={linkBtnStyle}
                onMouseEnter={e => { e.currentTarget.style.background = 'rgba(27, 79, 114, 0.05)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)'; }}
              >
                Dashboard da Direção <span>→</span>
              </button>
            </div>
          </div>

          {/* Ferramentas */}
          <div style={cardStyle}>
            <h3 style={subTitle}>Usar ferramentas de apoio</h3>
            <p style={{ fontSize: '14px', lineHeight: 1.7, color: '#4a5568', marginBottom: '12px' }}>
              Utilize artefatos práticos para apoiar um planejamento já em andamento, mesmo que ele não tenha sido criado integralmente neste sistema.
            </p>
            <p style={{ fontSize: '13px', lineHeight: 1.6, color: '#6b7280', marginBottom: '20px' }}>
              As ferramentas podem ser usadas de forma independente, conforme a necessidade do seu projeto ou processo.
            </p>
            <Button
              variant="outline"
              onClick={() => onNavigate('/ferramentas-apoio')}
              size="md"
              style={{ width: '100%', fontWeight: 600 }}
            >
              Acessar ferramentas de apoio
            </Button>
          </div>
        </div>
      </div>

      {/* PAINÉIS DE ACOMPANHAMENTO */}
      <div style={{ ...cardStyle, marginBottom: '32px' }}>
        <h2 style={{ ...sectionTitle, marginBottom: '8px' }}>Painéis de acompanhamento</h2>
        <p style={{ fontSize: '14px', color: '#4a5568', marginBottom: '8px' }}>Dashboards de Governança</p>
        <p style={{ fontSize: '14px', color: '#4a5568', marginBottom: '24px' }}>
          Acompanhamento consolidado de projetos estratégicos e pedidos da Direção.
        </p>

        <div style={{ display: 'flex', gap: '24px', marginBottom: '24px', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 200px', padding: '20px', background: 'rgba(27, 79, 114, 0.04)', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 700, color: '#1B4F72' }}>{estatisticas?.total_projetos ?? 0}</div>
            <div style={{ fontSize: '13px', color: '#4a5568', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Projetos Ativos</div>
          </div>
          <div style={{ flex: '1 1 200px', padding: '20px', background: 'rgba(27, 79, 114, 0.04)', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 700, color: '#1B4F72' }}>{estatisticas?.total_pedidos ?? 0}</div>
            <div style={{ fontSize: '13px', color: '#4a5568', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Pedidos da Direção</div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button
            onClick={onAbrirDashboardAreas}
            style={linkBtnStyle}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(27, 79, 114, 0.05)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)'; }}
          >
            <div>
              <div style={{ fontWeight: 600 }}>Dashboard das Áreas</div>
              <div style={{ fontSize: '13px', fontWeight: 400, color: '#6b7280', marginTop: '2px' }}>Gerencie os projetos estratégicos sob sua responsabilidade ou coordenação</div>
            </div>
            <span>→</span>
          </button>
          <button
            onClick={onAbrirDashboardDiretor}
            style={linkBtnStyle}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(27, 79, 114, 0.05)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)'; }}
          >
            <div>
              <div style={{ fontWeight: 600 }}>Dashboard da Direção</div>
              <div style={{ fontSize: '13px', fontWeight: 400, color: '#6b7280', marginTop: '2px' }}>Visão consolidada dos pedidos, prazos e status dos projetos estratégicos</div>
            </div>
            <span>→</span>
          </button>
        </div>

        <p style={{ fontSize: '13px', color: '#6b7280', marginTop: '16px', margin: '16px 0 0' }}>
          Dica: os pedidos da Direção são sincronizados automaticamente com os projetos acompanhados pelas áreas.
        </p>
      </div>

      {/* OUTRAS FORMAS DE COMEÇAR */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={sectionTitle}>Outras formas de começar</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <button
            onClick={() => onNavigate('/planejamento-estrategico/diagnostico')}
            style={{ ...cardStyle, cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s ease' }}
            onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 8px 24px rgba(27, 79, 114, 0.12)'; }}
            onMouseLeave={e => { e.currentTarget.style.boxShadow = '0 4px 16px rgba(27, 79, 114, 0.06)'; }}
          >
            <h3 style={{ ...subTitle, fontSize: '16px' }}>Diagnóstico Guiado</h3>
            <p style={{ fontSize: '14px', color: '#4a5568', lineHeight: 1.6, margin: 0 }}>
              Responda a perguntas orientadas e receba recomendações de modelos e ferramentas adequadas ao seu contexto.
            </p>
          </button>

          <button
            onClick={() => onNavigate('/planejamento-estrategico/modelos')}
            style={{ ...cardStyle, cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s ease' }}
            onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 8px 24px rgba(27, 79, 114, 0.12)'; }}
            onMouseLeave={e => { e.currentTarget.style.boxShadow = '0 4px 16px rgba(27, 79, 114, 0.06)'; }}
          >
            <h3 style={{ ...subTitle, fontSize: '16px' }}>Explorar Modelos</h3>
            <p style={{ fontSize: '14px', color: '#4a5568', lineHeight: 1.6, margin: 0 }}>
              Visualize todos os modelos disponíveis e escolha conforme sua necessidade.
            </p>
          </button>

          <button
            onClick={() => onNavigate('/planejamento-estrategico/modelos')}
            style={{ ...cardStyle, cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s ease' }}
            onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 8px 24px rgba(27, 79, 114, 0.12)'; }}
            onMouseLeave={e => { e.currentTarget.style.boxShadow = '0 4px 16px rgba(27, 79, 114, 0.06)'; }}
          >
            <h3 style={{ ...subTitle, fontSize: '16px' }}>Escolha Direta</h3>
            <p style={{ fontSize: '14px', color: '#4a5568', lineHeight: 1.6, margin: 0 }}>
              Se você já sabe qual ferramenta ou modelo deseja utilizar, acesse diretamente.
            </p>
          </button>
        </div>
      </div>

      {/* CTA FINAL */}
      <div style={{
        textAlign: 'center',
        padding: '40px 20px',
        marginBottom: '48px',
        background: 'rgba(27, 79, 114, 0.03)',
        borderRadius: '16px',
        border: '1px solid rgba(27, 79, 114, 0.08)'
      }}>
        <Button
          variant="primary"
          onClick={() => onNavigate('/planejamento-estrategico/painel')}
          size="lg"
          style={{
            background: 'linear-gradient(135deg, #1B4F72 0%, #2874A6 100%)',
            color: '#fff',
            padding: '18px 48px',
            borderRadius: '12px',
            border: 'none',
            fontWeight: 700,
            fontSize: '18px',
            cursor: 'pointer',
            boxShadow: '0 6px 24px rgba(27, 79, 114, 0.3)',
            transition: 'all 0.3s ease'
          }}
        >
          Explorar Planejamento Estratégico
        </Button>
      </div>
    </div>
  );
};

export default PlanejamentoLanding;
