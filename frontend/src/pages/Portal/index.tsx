import { useState } from 'react';
import type { ProductCode } from '../../types/portal.types';
import ProductsSidebar from '../../components/Portal/ProductsSidebar';
import PortalChat from '../../components/Portal/PortalChat';
import styles from './Portal.module.css';

export default function Portal() {
  const [selectedProduct, setSelectedProduct] = useState<ProductCode>('geral');

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
          onProductSelect={setSelectedProduct}
        />
        <PortalChat selectedProduct={selectedProduct} />
      </div>
    </div>
  );
}
