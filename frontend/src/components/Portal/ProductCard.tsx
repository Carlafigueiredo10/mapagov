import type { Product } from '../../types/portal.types';
import styles from './ProductCard.module.css';

interface ProductCardProps {
  product: Product;
  isActive: boolean;
  onClick: () => void;
}

export default function ProductCard({ product, isActive, onClick }: ProductCardProps) {
  return (
    <div
      className={`${styles.productCard} ${isActive ? styles.active : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
    >
      {product.code === 'geral' ? (
        <img
          src="/static/img/logo_mapa.png"
          alt="MapaGov"
          className={styles.productLogo}
        />
      ) : (
        <span className={styles.productIcon}>{product.icon}</span>
      )}

      <div className={styles.productTitle}>{product.title}</div>
      <div className={styles.productStatus}>{product.statusLabel}</div>
    </div>
  );
}
