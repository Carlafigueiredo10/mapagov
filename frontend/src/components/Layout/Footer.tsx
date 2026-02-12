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
              Sistema de Governança, Riscos e Conformidade para o Setor Público Brasileiro.
            </p>
            <p>
              Sistema desenvolvido pela Diretoria de Serviços de Aposentados e Pensionistas
              e de Órgãos Extintos (DECIPEX), unidade integrante do Ministério da Gestão
              e da Inovação em Serviços Públicos (MGI).
            </p>
          </div>

          <div>
            <h5>Institucional</h5>
            <ul>
              <li><Link to="/sobre">Sobre o MapaGov</Link></li>
              <li><a href="/#base-legal-preview">Base legal</a></li>
              <li><Link to="/funcionalidades">Governança do sistema</Link></li>
              <li><Link to="/legal/politica">Política de privacidade</Link></li>
              <li><Link to="/legal/termos">Termos de uso</Link></li>
            </ul>
          </div>

          <div>
            <h5>Sistema</h5>
            <ul>
              <li><Link to="/portal">Acessar portal</Link></li>
              <li><Link to="/funcionalidades">Funcionalidades</Link></li>
              <li><a href="/#roadmap">Roadmap</a></li>
              <li><Link to="/pop">Helena IA</Link></li>
            </ul>
          </div>

          <div>
            <h5>Suporte e Recursos</h5>
            <ul>
              <li><Link to="/pop">Assistente IA</Link></li>
              <li><Link to="/funcionalidades">Documentação</Link></li>
              <li><Link to="/fluxograma">Fluxogramas</Link></li>
              <li><Link to="/riscos">Análise de Riscos</Link></li>
            </ul>
          </div>

          <div>
            <h5>Transparência</h5>
            <ul>
              <li><a href="/#roadmap">Histórico de versões</a></li>
              <li><a href="/#roadmap">Próximos lançamentos</a></li>
              <li><Link to="/sobre">Fale conosco</Link></li>
            </ul>
          </div>
        </div>

        <div className={styles.footerBottom}>
          <p>&copy; 2025 MapaGov</p>
          <p>Plataforma oficial do Ministério da Gestão e da Inovação em Serviços Públicos.</p>
        </div>
      </div>
    </footer>
  );
}
