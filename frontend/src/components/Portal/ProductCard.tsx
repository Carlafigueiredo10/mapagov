import type { Product } from '../../types/portal.types';
import styles from './ProductCard.module.css';

interface ProductCardProps {
  product: Product;
  isActive: boolean;
  onClick: () => void;
}

export default function ProductCard({ product, isActive, onClick }: ProductCardProps) {
  const isDisabled = product.status === 'planejado';

  return (
    <div
      className={`${styles.productCard} ${isActive ? styles.active : ''} ${isDisabled ? styles.disabled : ''}`}
      onClick={isDisabled ? undefined : onClick}
      role={isDisabled ? undefined : 'button'}
      tabIndex={isDisabled ? -1 : 0}
      title={product.description}
      aria-disabled={isDisabled || undefined}
      onKeyDown={isDisabled ? undefined : (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
    >
      {product.code === 'geral' ? (
        <img
          src="/logo_mapa.png"
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
