// Header.tsx - Componente de cabeçalho reutilizável
import { Link } from 'react-router-dom';
import styles from './Header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        <Link to="/" className={styles.logo}>
          <img src="/static/logo_mapa.png" alt="MapaGov" className={styles.logoImg} />
          <div className={styles.logoText}>
            <span className={styles.logoTitle}>MapaGov</span>
            <span className={styles.logoSubtitle}>IA a Serviço da Governança Pública</span>
          </div>
        </Link>
        <ul className={styles.navLinks}>
          <li><a href="#sobre">Sobre</a></li>
          <li><a href="#funcionalidades">Funcionalidades</a></li>
          <li><a href="#roadmap">Roadmap</a></li>
          <li><a href="#base-legal">Base Legal</a></li>
          <li><Link to="/portal">Portal</Link></li>
        </ul>
      </nav>
    </header>
  );
}
