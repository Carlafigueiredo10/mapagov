import { Link } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import styles from './BaseLegalPage.module.css';

interface Doc {
  title: string;
  url: string | null;
  badge: 'pdf' | 'web' | 'pago' | 'indisponivel';
  note?: string;
}

interface Category {
  icon: string;
  title: string;
  docs: Doc[];
}

const CATEGORIES: Category[] = [
  {
    icon: '\u2696\uFE0F',
    title: 'Governan\u00e7a e gest\u00e3o p\u00fablica',
    docs: [
      {
        title: 'Decreto n.\u00ba 9.203/2017 \u2014 Pol\u00edtica de governan\u00e7a da administra\u00e7\u00e3o p\u00fablica federal',
        url: 'https://repositorio.cgu.gov.br/bitstream/1/33419/10/decreto_%20n_9203_22_novembro_2017.pdf',
        badge: 'pdf',
      },
      {
        title: 'Instru\u00e7\u00e3o Normativa Conjunta MP/CGU n.\u00ba 1/2016',
        url: 'https://www.gov.br/mj/pt-br/acesso-a-informacao/governanca/Gestao-de-Riscos/biblioteca/Normativos/instrucao-normativa-conjunta-no-1-de-10-de-maio-de-2016-imprensa-nacional.pdf/@@download/file',
        badge: 'pdf',
      },
      {
        title: 'Referencial B\u00e1sico de Governan\u00e7a Organizacional \u2014 TCU (2020)',
        url: 'https://portal.tcu.gov.br/data/files/0A/68/0D/A4/3A183710D046C8A7E18818A8/Referencial_basico_governanca_organizacional_3_edicao.pdf',
        badge: 'pdf',
      },
    ],
  },
  {
    icon: '\uD83D\uDEE1\uFE0F',
    title: 'Integridade p\u00fablica',
    docs: [
      {
        title: 'Decreto n.\u00ba 11.529/2023 \u2014 Sistema de Integridade, Transpar\u00eancia e Acesso \u00e0 Informa\u00e7\u00e3o',
        url: 'https://www.gov.br/cnen/pt-br/acesso-a-informacao/comites-internos/comite-gestor-de-integridade/Decreto11.529de16demaiode2023.pdf',
        badge: 'pdf',
      },
      {
        title: 'Portaria MGI n.\u00ba 6.725/2024 \u2014 Programa de Integridade do MGI',
        url: 'https://www.gov.br/gestao/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/pro-integridade/PortariaMGIN6.725de16deSetembrode2024.pdf',
        badge: 'pdf',
      },
      {
        title: 'Modelo de Maturidade em Integridade P\u00fablica \u2014 CGU (2023)',
        url: 'https://www.gov.br/cgu/pt-br/centrais-de-conteudo/noticias/2023/12/cgu-lanca-modelo-de-maturidade-inovador-para-implementar-e-avaliar-programas-de-integridade/modelodematuridadeemintegridadepublicaversao1.0.pdf',
        badge: 'pdf',
      },
    ],
  },
  {
    icon: '\uD83D\uDCCA',
    title: 'Gest\u00e3o de riscos \u2014 marco institucional (MGI)',
    docs: [
      {
        title: 'Resolu\u00e7\u00e3o CITARC/MGI n.\u00ba 1/2023 \u2014 Pol\u00edtica de Gest\u00e3o de Riscos do MGI',
        url: 'https://boletim.sigepe.gov.br/publicacao/detalhar/255141',
        badge: 'web',
        note: 'P\u00e1gina do BGP/SIGEPE \u2014 pode exigir download do PDF dentro do portal',
      },
      {
        title: 'Resolu\u00e7\u00e3o CITARC/MGI n.\u00ba 4/2024 \u2014 Aprova o Guia de Gest\u00e3o de Riscos do MGI',
        url: 'https://www.gov.br/gestao/pt-br/acesso-a-informacao/estrategia-e-governanca/estrutura-de-governanca/reunioes-e-decisoes/CITARC_Resolucao_4.pdf',
        badge: 'pdf',
      },
      {
        title: 'Resolu\u00e7\u00e3o CITARC/MGI n.\u00ba 5/2025 \u2014 Disciplina a Carteira de Riscos Estrat\u00e9gicos',
        url: 'https://www.gov.br/gestao/pt-br/acesso-a-informacao/estrategia-e-governanca/estrutura-de-governanca/reunioes-e-decisoes/CITARC_Resolucao_5.pdf',
        badge: 'pdf',
      },
      {
        title: 'Guia de Gest\u00e3o de Riscos do MGI (2024) \u2014 Metodologia institucional',
        url: 'https://www.gov.br/gestao/pt-br/acesso-a-informacao/estrategia-e-governanca/estrutura-de-governanca/citarc/guia_gr_mgi.pdf',
        badge: 'pdf',
      },
    ],
  },
  {
    icon: '\uD83D\uDD0D',
    title: 'Gest\u00e3o de riscos \u2014 referenciais t\u00e9cnicos',
    docs: [
      {
        title: 'ISO 31000 (2018) \u2014 Diretrizes internacionais de gest\u00e3o de riscos',
        url: 'https://www.iso.org/standard/65694.html',
        badge: 'pago',
        note: 'Norma dispon\u00edvel para compra no site oficial da ISO',
      },
      {
        title: 'ABNT NBR ISO 31073 (2022) \u2014 Terminologia aplic\u00e1vel \u00e0 gest\u00e3o de riscos',
        url: 'https://www.abntcatalogo.com.br/',
        badge: 'pago',
        note: 'Compra/consulta no Cat\u00e1logo ABNT',
      },
      {
        title: 'ABNT NBR ISO/IEC 31010 (2012) \u2014 T\u00e9cnicas de identifica\u00e7\u00e3o e an\u00e1lise de riscos',
        url: 'https://www.abntcatalogo.com.br/',
        badge: 'pago',
        note: 'Compra/consulta no Cat\u00e1logo ABNT',
      },
      {
        title: 'COSO ERM (2017) \u2014 Estrutura integrada de riscos, estrat\u00e9gia e desempenho',
        url: 'https://www.coso.org/enterprise-risk-management',
        badge: 'pago',
        note: 'P\u00e1gina oficial do COSO \u2014 \u00edntegra dispon\u00edvel mediante aquisi\u00e7\u00e3o',
      },
      {
        title: 'Referencial B\u00e1sico de Gest\u00e3o de Riscos \u2014 TCU (2018)',
        url: 'https://portal.tcu.gov.br/data/files/99/F2/81/06/E464E710ED4F42E7E18818A8/Referencial_basico_gestao_riscos.pdf',
        badge: 'pdf',
      },
      {
        title: 'Manual de Gest\u00e3o de Riscos \u2014 TCU (2020)',
        url: 'https://www.gov.br/governodigital/pt-br/seguranca-e-protecao-de-dados/gestao-de-riscos/arquivos/manual_gestao_riscos_tcu.pdf',
        badge: 'pdf',
      },
      {
        title: 'Metodologia de Gest\u00e3o de Riscos \u2014 CGU (2018)',
        url: 'https://www.gov.br/cgu/pt-br/assuntos/governanca/gestao-de-riscos/metodologia-de-gestao-de-riscos/metodologia-de-gestao-de-riscos.pdf',
        badge: 'pdf',
      },
    ],
  },
  {
    icon: '\uD83C\uDFE2',
    title: 'Estrutura organizacional, estrat\u00e9gia e processos',
    docs: [
      {
        title: 'Decreto n.\u00ba 12.102/2024 \u2014 Estrutura Regimental do MGI',
        url: 'https://legis.sigepe.gov.br/sigepe-bgp-ws-legis/legis-service/download/?id=0019573244-ALPDF%2F2024',
        badge: 'pdf',
      },
      {
        title: 'Resolu\u00e7\u00e3o CMG/MGI n.\u00ba 1/2023 \u2014 Planejamento Estrat\u00e9gico 2023\u20132027',
        url: 'https://www.gov.br/gestao/pt-br/acesso-a-informacao/estrategia-e-governanca/estrutura-de-governanca/comite-ministerial-de-governanca/Resoluon1.pdf',
        badge: 'pdf',
      },
      {
        title: 'Resolu\u00e7\u00e3o CMG/MGI n.\u00ba 2/2024 \u2014 Cadeia de Valor do MGI',
        url: 'https://www.gov.br/gestao/pt-br/acesso-a-informacao/estrategia-e-governanca/estrutura-de-governanca/comite-ministerial-de-governanca/Resoluon2.pdf',
        badge: 'pdf',
      },
      {
        title: 'Guia Pr\u00e1tico de Gest\u00e3o de Processos \u2014 MGI (2024)',
        url: 'https://www.gov.br/gestao/pt-br/acesso-a-informacao/estrategia-e-governanca/gestaodeprocessos/arquivos_pdf/GuiaPrticodeGestodeProcessosv1maiode20241.pdf',
        badge: 'pdf',
      },
      {
        title: 'Guia Pr\u00e1tico de Gest\u00e3o de Projetos \u2014 MGI (2025)',
        url: 'https://www.gov.br/gestao/pt-br/acesso-a-informacao/estrategia-e-governanca/planejamento_estrategico_arquivos/livros_guias_publicacoes/guia-pratico-de-projetos.pdf',
        badge: 'pdf',
      },
    ],
  },
  {
    icon: '\uD83D\uDCBB',
    title: 'Experi\u00eancia digital e comunica\u00e7\u00e3o',
    docs: [
      {
        title: 'Decreto n.\u00ba 10.332/2020 \u2014 Estrat\u00e9gia de Governo Digital',
        url: 'https://www.gov.br/defesa/pt-br/acesso-a-informacao/governanca-e-gestao/diretoria-de-governanca/egov/normativos/Decreto10332.pdf',
        badge: 'pdf',
      },
      {
        title: 'Decreto n.\u00ba 9.094/2017 \u2014 Simplifica\u00e7\u00e3o do atendimento ao usu\u00e1rio',
        url: 'https://repositorio.cgu.gov.br/bitstream/1/34011/8/Decreto_9.094_2017.pdf',
        badge: 'pdf',
      },
      {
        title: 'Lei n.\u00ba 13.460/2017 \u2014 Direitos dos usu\u00e1rios de servi\u00e7os p\u00fablicos',
        url: 'https://www.gov.br/capes/pt-br/centrais-de-conteudo/26062017-lei-no-13460-pdf',
        badge: 'pdf',
      },
      {
        title: 'Lei n.\u00ba 15.263/2025 \u2014 Pol\u00edtica Nacional de Linguagem Simples',
        url: 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15263.htm',
        badge: 'web',
      },
      {
        title: 'Design System Gov.br \u2014 Padr\u00f5es oficiais de interface e acessibilidade digital',
        url: 'https://www.gov.br/ds',
        badge: 'web',
        note: 'Documenta\u00e7\u00e3o web vigente \u2014 n\u00e3o h\u00e1 PDF \u00fanico consolidado',
      },
    ],
  },
];

const BADGE_LABELS: Record<Doc['badge'], string> = {
  pdf: 'PDF',
  web: 'WEB',
  pago: 'ACESSO PAGO',
  indisponivel: 'INDISPON\u00cdVEL',
};

const BADGE_STYLES: Record<Doc['badge'], string> = {
  pdf: 'badgePdf',
  web: 'badgeWeb',
  pago: 'badgePago',
  indisponivel: 'badgeIndisponivel',
};

export default function BaseLegalPage() {
  return (
    <Layout>
      <div className={styles.container}>
        <Link to="/" className={styles.backLink}>
          ← Voltar ao início
        </Link>

        <header className={styles.header}>
          <h1 className={styles.title}>Base Legal Integrada</h1>
          <p className={styles.subtitle}>
            Biblioteca de documentos normativos, referenciais técnicos e guias oficiais que
            fundamentam as práticas de governança, gestão de riscos e integridade no âmbito
            da administração pública federal.
          </p>
        </header>

        {CATEGORIES.map((cat) => (
          <section key={cat.title} className={styles.category}>
            <div className={styles.categoryHeader}>
              <span className={styles.categoryIcon}>{cat.icon}</span>
              <h2 className={styles.categoryTitle}>{cat.title}</h2>
            </div>
            <ul className={styles.docList}>
              {cat.docs.map((doc) => (
                <li key={doc.title} className={styles.docItem}>
                  <span className={`${styles.badge} ${styles[BADGE_STYLES[doc.badge]]}`}>
                    {BADGE_LABELS[doc.badge]}
                  </span>
                  <div>
                    {doc.url ? (
                      <a
                        href={doc.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.docLink}
                      >
                        {doc.title}
                      </a>
                    ) : (
                      <span className={styles.docLink}>{doc.title}</span>
                    )}
                    {doc.note && <span className={styles.note}>{doc.note}</span>}
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ))}


      </div>
    </Layout>
  );
}
