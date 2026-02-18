import type { ProductCode } from '../../types/portal.types';
import { products } from '../../data/products';
import ProductCard from './ProductCard';
import styles from './ProductsSidebar.module.css';

interface ProductsSidebarProps {
  selectedProduct: ProductCode;
  onProductSelect: (product: ProductCode) => void;
}

const STATUS_GROUPS = [
  { status: 'disponivel', label: null },
  { status: 'homologacao', label: 'Em homologação' },
  { status: 'desenvolvimento', label: 'Em desenvolvimento' },
  { status: 'planejado', label: 'Previstos' },
] as const;

export default function ProductsSidebar({ selectedProduct, onProductSelect }: ProductsSidebarProps) {
  return (
    <aside className={styles.sidebar}>
      <h3 className={styles.title}>Produtos MapaGov</h3>

      <div className={styles.productsList}>
        {STATUS_GROUPS.map(({ status, label }) => {
          const group = products.filter((p) => p.status === status);
          if (group.length === 0) return null;
          return (
            <div key={status}>
              {label && <div className={styles.groupLabel}>{label}</div>}
              {group.map((product) => (
                <ProductCard
                  key={product.code}
                  product={product}
                  isActive={selectedProduct === product.code}
                  onClick={() => onProductSelect(product.code)}
                />
              ))}
            </div>
          );
        })}
      </div>
    </aside>
  );
}
