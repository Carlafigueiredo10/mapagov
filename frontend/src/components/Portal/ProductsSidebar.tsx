import type { ProductCode } from '../../types/portal.types';
import { products } from '../../data/products';
import ProductCard from './ProductCard';
import styles from './ProductsSidebar.module.css';

interface ProductsSidebarProps {
  selectedProduct: ProductCode;
  onProductSelect: (product: ProductCode) => void;
}

export default function ProductsSidebar({ selectedProduct, onProductSelect }: ProductsSidebarProps) {
  return (
    <aside className={styles.sidebar}>
      <h3 className={styles.title}>Produtos MapaGov</h3>

      <div className={styles.productsList}>
        {products.map((product) => (
          <ProductCard
            key={product.code}
            product={product}
            isActive={selectedProduct === product.code}
            onClick={() => onProductSelect(product.code)}
          />
        ))}
      </div>
    </aside>
  );
}
