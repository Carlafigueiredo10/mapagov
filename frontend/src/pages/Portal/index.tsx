import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { ProductCode } from '../../types/portal.types';
import { products } from '../../data/products';
import ProductsSidebar from '../../components/Portal/ProductsSidebar';
import PortalChat from '../../components/Portal/PortalChat';
import styles from './Portal.module.css';

export default function Portal() {
  const navigate = useNavigate();
  const [selectedProduct, setSelectedProduct] = useState<ProductCode>('geral');

  const handleProductSelect = (code: ProductCode) => {
    const product = products.find((p) => p.code === code);
    if (product?.route) {
      navigate(product.route);
    } else {
      setSelectedProduct(code);
    }
  };

  return (
    <div className={styles.portalPage}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <a href="/" className={styles.logo}>
            <span className={styles.logoText}>MapaGov</span>
          </a>
          <nav className={styles.headerNav}>
            <a href="/" className={styles.navLink}>Início</a>
          </nav>
        </div>
      </header>

      {/* Main Container */}
      <div className={styles.mainContainer}>
        <ProductsSidebar
          selectedProduct={selectedProduct}
          onProductSelect={handleProductSelect}
        />
        <PortalChat selectedProduct={selectedProduct} />
      </div>
    </div>
  );
}
