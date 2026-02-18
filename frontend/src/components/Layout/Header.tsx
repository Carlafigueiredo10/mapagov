// Header.tsx - Componente de cabeçalho reutilizável
import { Link } from 'react-router-dom';
import styles from './Header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        <Link to="/" className={styles.logo}>
          <img src="/logo_mapa.png" alt="MapaGov" className={styles.logoImg} />
          <div className={styles.logoText}>
            <span className={styles.logoTitle}>MapaGov</span>
            <span className={styles.logoSubtitle}>IA a Serviço da Governança Pública</span>
          </div>
        </Link>
        <ul className={styles.navLinks}>
          <li><Link to="/sobre">Sobre</Link></li>
          <li><Link to="/funcionalidades">Funcionalidades</Link></li>
          <li><Link to="/base-legal">Base Legal</Link></li>
          <li><Link to="/portal">Iniciar trabalho</Link></li>
        </ul>
      </nav>
    </header>
  );
}
