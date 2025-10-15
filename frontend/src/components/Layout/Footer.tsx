// Footer.tsx - Componente de rodapé reutilizável
import { Link } from 'react-router-dom';
import styles from './Footer.module.css';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.footerGrid}>
          <div className={styles.footerBrand}>
            <h4>MapaGov</h4>
            <p>
              Sistema completo de Governança, Riscos e Conformidade desenvolvido especificamente
              para as necessidades do setor público brasileiro.
            </p>
            <p>
              Desenvolvido pela DECIPEX/MGI. Baseado em padrões DECIPEX/MGI, referenciais TCU/CGU
              e normas internacionais.
            </p>
          </div>

          <div>
            <h5>Sistema</h5>
            <ul>
              <li><Link to="/portal">Portal</Link></li>
              <li><a href="#funcionalidades">Funcionalidades</a></li>
              <li><a href="#roadmap">Roadmap</a></li>
              <li><Link to="/chat">Helena IA</Link></li>
              <li><a href="#base-legal">Base Legal</a></li>
            </ul>
          </div>

          <div>
            <h5>Recursos</h5>
            <ul>
              <li><Link to="/chat">Assistente IA</Link></li>
              <li><Link to="/fluxograma">Fluxogramas</Link></li>
              <li><Link to="/riscos">Análise de Riscos</Link></li>
              <li><a href="#roadmap">Próximos Lançamentos</a></li>
              <li><a href="#base-legal">Base Legal</a></li>
            </ul>
          </div>

          <div>
            <h5>Contato</h5>
            <ul>
              <li><Link to="/portal">Demonstração</Link></li>
              <li><Link to="/chat">Começar Agora</Link></li>
              <li><a href="#funcionalidades">Recursos</a></li>
              <li><Link to="/portal">Suporte</Link></li>
            </ul>
          </div>
        </div>

        <div className={styles.footerBottom}>
          <p>&copy; 2025 MapaGov. Sistema de Governança, Riscos e Conformidade para o Setor Público Brasileiro.</p>
        </div>
      </div>
    </footer>
  );
}
