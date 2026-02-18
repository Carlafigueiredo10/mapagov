// Header.tsx - Componente de cabeçalho reutilizável
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import styles from './Header.module.css';

export default function Header() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

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
        {isAuthenticated && user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginLeft: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ fontWeight: 600, fontSize: 13, color: '#1B4F72' }}>
                {user.nome_completo?.split(' ')[0] || user.email}
              </span>
              <span style={{
                width: 8, height: 8, borderRadius: '50%', background: '#2e7d32',
                display: 'inline-block',
              }} />
              <span style={{ fontSize: 11, color: '#666' }}>logado</span>
            </div>
            <button
              onClick={handleLogout}
              style={{
                background: 'transparent', border: '1px solid #ccc', borderRadius: 4,
                padding: '4px 10px', fontSize: 12, color: '#666', cursor: 'pointer',
              }}
            >
              Sair
            </button>
          </div>
        )}
      </nav>
    </header>
  );
}
