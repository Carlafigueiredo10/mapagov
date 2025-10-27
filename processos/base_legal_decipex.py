"""
Sugestor de Base Legal adaptado ao contexto DECIPEX
Versão 2.2 - Focado em Gestão de Pessoas, Benefícios e Governança
Sem normas de Licitações, Compras, TI ou Orçamento
"""

import re
from functools import lru_cache
from typing import Dict, List, Any


class FormatadorUtils:
    """Utilitários para formatação de dados (subset local)"""

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """Remove acentos e caracteres especiais"""
        import unicodedata
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
        return texto.lower()


class BaseLegalSuggestorDECIPEx:
    """
    Sugestor de Base Legal para o contexto DECIPEX
    Foco: Benefícios, Gestão de Pessoas, Processos Administrativos, Governança
    """

    def __init__(self):
        """Inicializa sugestor com biblioteca focada no DECIPEX"""
        self.biblioteca = self._carregar_biblioteca()
        self.grupos_labels = {
            "beneficios": "🩺 Benefícios e Saúde do Servidor",
            "pessoas": "👥 Gestão de Pessoas e Conduta Funcional",
            "processos": "⚙️ Gestão Processual e Atendimento",
            "riscos": "🧾 Governança, Riscos e Controles Internos",
            "dados": "🔐 Proteção de Dados e Segurança da Informação",
            "transparencia": "🔍 Transparência e Acesso à Informação"
        }

    @lru_cache(maxsize=1)
    def _carregar_biblioteca(self) -> Dict[str, Any]:
        """Carrega biblioteca estática de normas relevantes ao DECIPEX (cached)"""
        return {
            "normas": [
                # ===== 1. BENEFÍCIOS E SAÚDE DO SERVIDOR =====
                {
                    "id": "norm_001",
                    "nome_curto": "IN 97/2022",
                    "nome_completo": "Instrução Normativa SGP/SEDGG/ME nº 97, de 26 de dezembro de 2022",
                    "artigos": "Art. 34-42",
                    "palavras_chave": ["ressarcimento", "plano saude", "auxilio saude", "assistencia suplementar", "aposentado"],
                    "areas": ["CGBEN"],
                    "hierarquia": 3,
                    "grupo": "beneficios"
                },
                {
                    "id": "norm_002",
                    "nome_curto": "Lei 8112/90 - Benefícios",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 215-230",
                    "palavras_chave": ["pensao", "auxilio funeral", "auxilio natalidade", "assistencia pre escolar", "servidor publico"],
                    "areas": ["CGBEN", "todas"],
                    "hierarquia": 1,
                    "grupo": "beneficios"
                },
                {
                    "id": "norm_003",
                    "nome_curto": "Decreto 4978/2004",
                    "nome_completo": "Decreto nº 4.978, de 3 de fevereiro de 2004",
                    "artigos": "Todos",
                    "palavras_chave": ["assistencia saude", "servidor", "dependente", "ressarcimento", "plano saude"],
                    "areas": ["CGBEN"],
                    "hierarquia": 2,
                    "grupo": "beneficios"
                },
                {
                    "id": "norm_004",
                    "nome_curto": "Lei 11784/2008",
                    "nome_completo": "Lei nº 11.784, de 22 de setembro de 2008",
                    "artigos": "Art. 139-142",
                    "palavras_chave": ["avaliacao desempenho", "progressao", "promocao", "merito"],
                    "areas": ["DIGEP"],
                    "hierarquia": 1,
                    "grupo": "beneficios"
                },
                {
                    "id": "norm_005",
                    "nome_curto": "Portaria 1675/2018",
                    "nome_completo": "Portaria GM/MS nº 1.675, de 7 de junho de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["pericia medica", "licenca saude", "atestado", "junta medica"],
                    "areas": ["DIGEP"],
                    "hierarquia": 3,
                    "grupo": "beneficios"
                },
                {
                    "id": "norm_006",
                    "nome_curto": "IN 02/2018",
                    "nome_completo": "Instrução Normativa SEGES/MPDG nº 2, de 30 de março de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["consignacao", "desconto", "folha pagamento", "margem consignavel"],
                    "areas": ["CGPAG"],
                    "hierarquia": 3,
                    "grupo": "beneficios"
                },

                # ===== 2. GESTÃO DE PESSOAS E CONDUTA FUNCIONAL =====
                {
                    "id": "norm_007",
                    "nome_curto": "Decreto 9991/2019",
                    "nome_completo": "Decreto nº 9.991, de 28 de agosto de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["capacitacao", "desenvolvimento", "gestao pessoas", "politica nacional", "treinamento"],
                    "areas": ["DIGEP"],
                    "hierarquia": 2,
                    "grupo": "pessoas"
                },
                {
                    "id": "norm_008",
                    "nome_curto": "Portaria 424/2020",
                    "nome_completo": "Portaria SGP/SEDGG/ME nº 424, de 27 de março de 2020",
                    "artigos": "Todos",
                    "palavras_chave": ["teletrabalho", "trabalho remoto", "home office"],
                    "areas": ["DIGEP"],
                    "hierarquia": 3,
                    "grupo": "pessoas"
                },
                {
                    "id": "norm_009",
                    "nome_curto": "IN 05/2017",
                    "nome_completo": "Instrução Normativa SGP/MP nº 5, de 26 de maio de 2017",
                    "artigos": "Todos",
                    "palavras_chave": ["horario flexivel", "jornada", "banco horas"],
                    "areas": ["DIGEP"],
                    "hierarquia": 3,
                    "grupo": "pessoas"
                },
                {
                    "id": "norm_010",
                    "nome_curto": "Decreto 1171/94",
                    "nome_completo": "Decreto nº 1.171, de 22 de junho de 1994",
                    "artigos": "Todos",
                    "palavras_chave": ["codigo etica", "conduta", "deveres", "servidor publico"],
                    "areas": ["todas"],
                    "hierarquia": 2,
                    "grupo": "pessoas"
                },
                {
                    "id": "norm_011",
                    "nome_curto": "Lei Inclusão",
                    "nome_completo": "Lei nº 13.146, de 6 de julho de 2015",
                    "artigos": "Todos",
                    "palavras_chave": ["inclusao", "pcd", "acessibilidade", "pessoa deficiencia"],
                    "areas": ["DIGEP", "todas"],
                    "hierarquia": 1,
                    "grupo": "pessoas"
                },
                {
                    "id": "norm_012",
                    "nome_curto": "Lei 8112/90 - Férias",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 77-80",
                    "palavras_chave": ["ferias", "recesso", "afastamento", "servidor"],
                    "areas": ["DIGEP", "todas"],
                    "hierarquia": 1,
                    "grupo": "pessoas"
                },
                {
                    "id": "norm_013",
                    "nome_curto": "Lei 8112/90 - Licenças",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 81-116",
                    "palavras_chave": ["licenca", "afastamento", "licenca capacitacao", "licenca saude", "maternidade"],
                    "areas": ["DIGEP", "todas"],
                    "hierarquia": 1,
                    "grupo": "pessoas"
                },
                {
                    "id": "norm_014",
                    "nome_curto": "Lei 11091/2005",
                    "nome_completo": "Lei nº 11.091, de 12 de janeiro de 2005",
                    "artigos": "Todos",
                    "palavras_chave": ["carreira tecnico administrativa", "universidade", "ifes"],
                    "areas": ["DIGEP"],
                    "hierarquia": 1,
                    "grupo": "pessoas"
                },

                # ===== 3. GESTÃO PROCESSUAL E ATENDIMENTO =====
                {
                    "id": "norm_015",
                    "nome_curto": "Lei 9784/99",
                    "nome_completo": "Lei nº 9.784, de 29 de janeiro de 1999",
                    "artigos": "Todos",
                    "palavras_chave": ["processo administrativo", "prazo", "atendimento", "defesa", "devido processo"],
                    "areas": ["COATE", "todas"],
                    "hierarquia": 1,
                    "grupo": "processos"
                },
                {
                    "id": "norm_016",
                    "nome_curto": "Decreto 9094/2017",
                    "nome_completo": "Decreto nº 9.094, de 17 de julho de 2017",
                    "artigos": "Todos",
                    "palavras_chave": ["simplificacao", "usuario", "servico publico", "desburocratizacao"],
                    "areas": ["COATE", "todas"],
                    "hierarquia": 2,
                    "grupo": "processos"
                },
                {
                    "id": "norm_017",
                    "nome_curto": "IN 65/2021",
                    "nome_completo": "Instrução Normativa SEGES/ME nº 65, de 7 de julho de 2021",
                    "artigos": "Todos",
                    "palavras_chave": ["processo eletronico", "sei", "tramitacao", "documento digital"],
                    "areas": ["todas"],
                    "hierarquia": 3,
                    "grupo": "processos"
                },
                {
                    "id": "norm_018",
                    "nome_curto": "Decreto 10139/2019",
                    "nome_completo": "Decreto nº 10.139, de 28 de novembro de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["revisao atos", "desburocratizacao", "simplificacao"],
                    "areas": ["todas"],
                    "hierarquia": 2,
                    "grupo": "processos"
                },
                {
                    "id": "norm_019",
                    "nome_curto": "Portaria 57/2019",
                    "nome_completo": "Portaria ME nº 57, de 4 de fevereiro de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["gestao processos", "mapeamento", "bpm", "modelagem"],
                    "areas": ["todas"],
                    "hierarquia": 3,
                    "grupo": "processos"
                },

                # ===== 4. GOVERNANÇA, RISCOS E CONTROLES INTERNOS =====
                {
                    "id": "norm_020",
                    "nome_curto": "Decreto 9203/2017",
                    "nome_completo": "Decreto nº 9.203, de 22 de novembro de 2017",
                    "artigos": "Todos",
                    "palavras_chave": ["governanca publica", "gestao riscos", "accountability", "controles"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 2,
                    "grupo": "riscos"
                },
                {
                    "id": "norm_021",
                    "nome_curto": "IN Conjunta 01/2016",
                    "nome_completo": "Instrução Normativa Conjunta CGU/MP nº 01, de 10 de maio de 2016",
                    "artigos": "Todos",
                    "palavras_chave": ["controles internos", "riscos", "integridade", "gestao riscos"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 3,
                    "grupo": "riscos"
                },
                {
                    "id": "norm_022",
                    "nome_curto": "Portaria Interministerial 140/2006",
                    "nome_completo": "Portaria Interministerial MF/CGU/MP nº 140, de 16 de março de 2006",
                    "artigos": "Todos",
                    "palavras_chave": ["auditoria", "controles internos", "gestao"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 3,
                    "grupo": "riscos"
                },
                {
                    "id": "norm_023",
                    "nome_curto": "IN TCU 84/2020",
                    "nome_completo": "Instrução Normativa TCU nº 84, de 22 de abril de 2020",
                    "artigos": "Todos",
                    "palavras_chave": ["auditoria interna", "governanca", "controles", "gestao riscos"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 4,
                    "grupo": "riscos"
                },
                {
                    "id": "norm_024",
                    "nome_curto": "Acórdão TCU 1078/2023",
                    "nome_completo": "Acórdão TCU nº 1078, de 2023",
                    "artigos": "Todos",
                    "palavras_chave": ["controles", "auditoria", "prestacao contas", "tcu", "governanca"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 4,
                    "grupo": "riscos"
                },
                {
                    "id": "norm_025",
                    "nome_curto": "Lei 12846/2013",
                    "nome_completo": "Lei nº 12.846, de 1º de agosto de 2013",
                    "artigos": "Todos",
                    "palavras_chave": ["anticorrupcao", "integridade", "compliance", "lei anticorrupcao"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 1,
                    "grupo": "riscos"
                },
                {
                    "id": "norm_026",
                    "nome_curto": "Portaria CGU 909/2015",
                    "nome_completo": "Portaria CGU nº 909, de 16 de abril de 2015",
                    "artigos": "Todos",
                    "palavras_chave": ["controles internos", "auditoria", "cgu", "gestao"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 3,
                    "grupo": "riscos"
                },
                {
                    "id": "norm_027",
                    "nome_curto": "Decreto 9739/2019",
                    "nome_completo": "Decreto nº 9.739, de 28 de março de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["medidas protetivas", "integridade", "combate corrupcao"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 2,
                    "grupo": "riscos"
                },

                # ===== 5. PROTEÇÃO DE DADOS E SEGURANÇA DA INFORMAÇÃO =====
                {
                    "id": "norm_028",
                    "nome_curto": "LGPD",
                    "nome_completo": "Lei nº 13.709, de 14 de agosto de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["dados pessoais", "privacidade", "lgpd", "protecao dados"],
                    "areas": ["CGCAF", "todas"],
                    "hierarquia": 1,
                    "grupo": "dados"
                },
                {
                    "id": "norm_029",
                    "nome_curto": "Decreto 10046/2019",
                    "nome_completo": "Decreto nº 10.046, de 9 de outubro de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["governanca dados", "interoperabilidade", "compartilhamento dados"],
                    "areas": ["CGCAF", "todas"],
                    "hierarquia": 2,
                    "grupo": "dados"
                },
                {
                    "id": "norm_030",
                    "nome_curto": "Portaria 443/2018",
                    "nome_completo": "Portaria GM/MD nº 443, de 28 de fevereiro de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["seguranca informacao", "ciberseguranca", "dsic"],
                    "areas": ["todas"],
                    "hierarquia": 3,
                    "grupo": "dados"
                },

                # ===== 6. TRANSPARÊNCIA E ACESSO À INFORMAÇÃO =====
                {
                    "id": "norm_031",
                    "nome_curto": "LAI",
                    "nome_completo": "Lei nº 12.527, de 18 de novembro de 2011",
                    "artigos": "Todos",
                    "palavras_chave": ["acesso informacao", "transparencia", "lai", "publicidade"],
                    "areas": ["todas"],
                    "hierarquia": 1,
                    "grupo": "transparencia"
                },
                {
                    "id": "norm_032",
                    "nome_curto": "Decreto 7724/2012",
                    "nome_completo": "Decreto nº 7.724, de 16 de maio de 2012",
                    "artigos": "Todos",
                    "palavras_chave": ["sic", "publicidade", "dados abertos", "transparencia", "esic"],
                    "areas": ["todas"],
                    "hierarquia": 2,
                    "grupo": "transparencia"
                },
                {
                    "id": "norm_033",
                    "nome_curto": "Decreto 11129/2022",
                    "nome_completo": "Decreto nº 11.129, de 11 de julho de 2022",
                    "artigos": "Todos",
                    "palavras_chave": ["simplificacao", "burocracia", "governanca", "eficiencia"],
                    "areas": ["todas"],
                    "hierarquia": 2,
                    "grupo": "transparencia"
                },
            ]
        }

    def _normalizar_keywords(self, texto: str) -> List[str]:
        """Normaliza e extrai keywords de um texto"""
        texto_limpo = FormatadorUtils.normalizar_texto(texto)
        texto_limpo = re.sub(r'[^a-z0-9\s]', ' ', texto_limpo)
        palavras = texto_limpo.split()
        palavras = [p for p in palavras if len(p) > 3]
        return list(set(palavras))

    def _calcular_score_norma(self, norma: Dict[str, Any], contexto_keywords: List[str], area_codigo: str) -> float:
        """Calcula score de relevância de uma norma"""
        score = 0.0

        # Match de keywords (peso 60)
        keywords_norma = norma.get('palavras_chave', [])
        matches = sum(1 for kw in contexto_keywords if any(kw in nkw for nkw in keywords_norma))

        if len(contexto_keywords) > 0:
            score += (matches / len(contexto_keywords)) * 60

        # Match de área (peso 20)
        areas_norma = norma.get('areas', [])
        if 'todas' in areas_norma or area_codigo in areas_norma:
            score += 20

        # Hierarquia (peso 20) - quanto menor a hierarquia, maior a prioridade
        hierarquia = norma.get('hierarquia', 5)
        score_hierarquia = ((6 - hierarquia) / 5) * 20
        score += score_hierarquia

        return min(score, 100.0)

    def sugerir_base_legal(self, contexto: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Sugere base legal baseada no contexto do processo

        Args:
            contexto: Dict com:
                - nome_processo: str
                - area_codigo: str
                - sistemas: List[str] (opcional)
                - objetivo: str (opcional)

        Returns:
            List[Dict] com top 3 sugestões:
                - nome_curto: str
                - nome_completo: str
                - artigos: str
                - confianca: float (0-100)
                - fonte: str ("biblioteca")
                - grupo: str ("beneficios", "pessoas", etc.)
                - label: str ("🩺 Benefícios e Saúde do Servidor", etc.)
        """
        try:
            # Extrair keywords do contexto
            texto_contexto = f"{contexto.get('nome_processo', '')} {contexto.get('objetivo', '')}"
            if contexto.get('sistemas'):
                texto_contexto += " " + " ".join(contexto.get('sistemas', []))

            keywords = self._normalizar_keywords(texto_contexto)
            area_codigo = contexto.get('area_codigo', '')

            # Calcular scores para todas as normas
            normas_com_score = []
            for norma in self.biblioteca['normas']:
                score = self._calcular_score_norma(norma, keywords, area_codigo)

                if score > 0:
                    normas_com_score.append({
                        'nome_curto': norma['nome_curto'],
                        'nome_completo': norma['nome_completo'],
                        'artigos': norma['artigos'],
                        'confianca': round(score, 2),
                        'fonte': 'biblioteca',
                        'grupo': norma['grupo'],
                        'label': self.grupos_labels.get(norma['grupo'], norma['grupo'])
                    })

            # Ordenar por score decrescente
            normas_com_score.sort(key=lambda x: x['confianca'], reverse=True)

            # Retornar top 3 (ou fallback se vazio)
            if not normas_com_score:
                return [{
                    'nome_curto': 'Lei 9784/99',
                    'nome_completo': 'Lei nº 9.784, de 29 de janeiro de 1999',
                    'artigos': 'Todos',
                    'confianca': 50.0,
                    'fonte': 'biblioteca',
                    'grupo': 'processos',
                    'label': self.grupos_labels['processos']
                }]

            return normas_com_score[:3]

        except Exception as e:
            print(f"Erro ao sugerir base legal: {e}")
            return []

    def buscar_por_palavra_chave(self, termo: str) -> List[Dict[str, Any]]:
        """
        Busca normas por palavra-chave específica

        Args:
            termo: Termo a ser buscado

        Returns:
            Lista de normas que contêm a palavra-chave
        """
        termo_normalizado = FormatadorUtils.normalizar_texto(termo)
        resultados = []

        for norma in self.biblioteca['normas']:
            keywords_norma = norma.get('palavras_chave', [])

            if any(termo_normalizado in kw for kw in keywords_norma):
                resultados.append({
                    'nome_curto': norma['nome_curto'],
                    'nome_completo': norma['nome_completo'],
                    'artigos': norma['artigos'],
                    'confianca': 100.0,
                    'fonte': 'biblioteca',
                    'grupo': norma['grupo'],
                    'label': self.grupos_labels.get(norma['grupo'], norma['grupo'])
                })

        return resultados

    def obter_normas_por_area(self, area_codigo: str) -> List[Dict[str, Any]]:
        """
        Retorna todas as normas aplicáveis a uma área específica

        Args:
            area_codigo: Código da área (ex: "CGBEN", "CGPAG")

        Returns:
            Lista de normas da área, ordenadas por hierarquia
        """
        resultados = []

        for norma in self.biblioteca['normas']:
            areas_norma = norma.get('areas', [])

            if 'todas' in areas_norma or area_codigo in areas_norma:
                resultados.append({
                    'nome_curto': norma['nome_curto'],
                    'nome_completo': norma['nome_completo'],
                    'artigos': norma['artigos'],
                    'hierarquia': norma['hierarquia'],
                    'grupo': norma['grupo'],
                    'label': self.grupos_labels.get(norma['grupo'], norma['grupo'])
                })

        # Ordenar por hierarquia (Lei > Decreto > IN)
        resultados.sort(key=lambda x: x['hierarquia'])

        return resultados

    def obter_grupos_normas(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna normas agrupadas por categoria

        Returns:
            Dict com estrutura:
            {
                "beneficios": {
                    "label": "🩺 Benefícios e Saúde do Servidor",
                    "itens": [norma1, norma2, ...]
                },
                ...
            }
        """
        grupos = {}

        for norma in self.biblioteca['normas']:
            grupo = norma['grupo']

            if grupo not in grupos:
                grupos[grupo] = {
                    'label': self.grupos_labels.get(grupo, grupo),
                    'itens': []
                }

            grupos[grupo]['itens'].append({
                'nome_curto': norma['nome_curto'],
                'nome_completo': norma['nome_completo'],
                'artigos': norma['artigos'],
                'hierarquia': norma['hierarquia']
            })

        # Ordenar itens dentro de cada grupo por hierarquia
        for grupo in grupos.values():
            grupo['itens'].sort(key=lambda x: x['hierarquia'])

        return grupos
