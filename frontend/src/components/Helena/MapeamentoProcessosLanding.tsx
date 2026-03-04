/**
 * MapeamentoProcessosLanding - Painel operacional "Meus POPs"
 *
 * Rota: /pop/meus
 * Tela de gestão: criar, retomar, clonar POPs.
 * Conteúdo educacional foi movido para GuiaMapeamentoLanding (/pop).
 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen } from 'lucide-react';
import styles from './MapeamentoProcessosLanding.module.css';
import PopHubSection from './PopHubSection';

interface MapeamentoProcessosLandingProps {
  onIniciar: () => void;
  onRetomar: (uuid: string) => void;
  onRevisar: (uuid: string) => void;
  onClonar: (popData: Record<string, unknown>) => void;
}

const MapeamentoProcessosLanding: React.FC<MapeamentoProcessosLandingProps> = ({
  onIniciar,
  onRetomar,
  onRevisar,
  onClonar,
}) => {
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      {/* Cabeçalho */}
      <header className={styles.header}>
        <h1 className={styles.title}>Mapeamento de Atividades</h1>
      </header>

      {/* Banner prevenção — consultar catálogo antes de criar */}
      <div className={styles.catalogoBanner}>
        <BookOpen size={20} />
        <div className={styles.catalogoBannerContent}>
          <span>
            Antes de registrar uma nova atividade, consulte o catálogo de Procedimentos
            Operacionais Padrão (POPs) e verifique se ela já está mapeada na sua
            Coordenação-Geral.
          </span>
          <span className={styles.catalogoBannerSub}>
            Caso não esteja registrada, você poderá realizar o mapeamento da atividade.
          </span>
          <button
            type="button"
            className={styles.catalogoBannerLink}
            onClick={() => navigate('/catalogo')}
          >
            Acessar catálogo →
          </button>
        </div>
      </div>

      {/* Hub de gestão documental */}
      <PopHubSection
        onCriarNovo={onIniciar}
        onRetomar={onRetomar}
        onRevisar={onRevisar}
        onClonar={onClonar}
      />

      {/* Links de navegação */}
      <section className={styles.linksSection}>
        <Link to="/pop" className={styles.guiaLink}>
          Precisa de ajuda para mapear? Acessar guia →
        </Link>
        <Link to="/catalogo" className={styles.catalogoLinkFull}>
          Consultar catálogo institucional →
        </Link>
      </section>
    </div>
  );
};

export default MapeamentoProcessosLanding;
