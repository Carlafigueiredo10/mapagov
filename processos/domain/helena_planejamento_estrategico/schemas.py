"""
Schemas e Configurações - Helena Planejamento Estratégico

Contém:
- EstadoPlanejamento: Enum de estados da máquina
- MODELOS_ESTRATEGICOS: Configuração dos 7 modelos
- PERGUNTAS_DIAGNOSTICO: Perguntas do diagnóstico guiado
"""
from enum import Enum
from typing import Dict, List, Any


# ============================================================================
# ENUMS - Estados da Conversa
# ============================================================================

class EstadoPlanejamento(str, Enum):
    """Estados da máquina de estados"""
    BOAS_VINDAS = "boas_vindas"
    ESCOLHA_MODO = "escolha_modo"  # diagnostico | explorar | direto

    # Fluxo Diagnóstico
    DIAGNOSTICO_P1 = "diagnostico_p1"  # maturidade
    DIAGNOSTICO_P2 = "diagnostico_p2"  # horizonte
    DIAGNOSTICO_P3 = "diagnostico_p3"  # contexto
    DIAGNOSTICO_P4 = "diagnostico_p4"  # equipe
    DIAGNOSTICO_P5 = "diagnostico_p5"  # objetivo
    RECOMENDACAO = "recomendacao"

    # Construção do Planejamento
    CONTEXTO_ORGANIZACIONAL = "contexto_organizacional"
    CONSTRUCAO_MODELO = "construcao_modelo"
    REFINAMENTO = "refinamento"
    REVISAO = "revisao"
    CONFIRMACAO = "confirmacao"
    FINALIZADO = "finalizado"


# ============================================================================
# CONFIGURAÇÃO DOS MODELOS ESTRATÉGICOS
# ============================================================================

MODELOS_ESTRATEGICOS: Dict[str, Dict[str, Any]] = {
    'tradicional': {
        'nome': 'Planejamento Estratégico Tradicional',
        'nome_curto': 'Estratégico Clássico',
        'descricao': 'Modelo normativo baseado em Missão, Visão, Valores e Objetivos institucionais. Padrão na APF.',
        'icone': '🏛️',
        'complexidade': 'media',
        'prazo': 'longo',
        'maturidade': 'intermediario',
        'tags': ['formal', 'institucional', 'abrangente'],
        'componentes': ['Missão', 'Visão', 'Valores', 'Objetivos Estratégicos', 'Metas', 'Indicadores'],
        'vantagens_publico': [
            'Alinhado com normativos do TCU e CGU',
            'Facilita prestação de contas',
            'Linguagem conhecida na APF'
        ],
        'quando_usar': [
            'Elaboração de PPA/LOA',
            'Planejamento institucional completo',
            'Exigência normativa'
        ],
        'estrutura_inicial': {
            'missao': '',
            'visao': '',
            'valores': [],
            'objetivos_estrategicos': []
        }
    },
    'bsc': {
        'nome': 'Balanced Scorecard Público',
        'nome_curto': 'BSC Público',
        'descricao': 'Framework de gestão estratégica com 4 perspectivas adaptadas para valor público.',
        'icone': '📊',
        'complexidade': 'alta',
        'prazo': 'longo',
        'maturidade': 'avancado',
        'tags': ['indicadores', 'perspectivas', 'mapa estratégico'],
        'componentes': ['Perspectivas', 'Objetivos', 'Indicadores', 'Metas', 'Iniciativas', 'Mapa Estratégico'],
        'vantagens_publico': [
            'Visão integrada da organização',
            'Foco em resultados para sociedade',
            'Casos de sucesso no TCU e ministérios'
        ],
        'quando_usar': [
            'Organizações com maturidade em gestão',
            'Necessidade de painel de indicadores',
            'Alinhamento entre áreas'
        ],
        'estrutura_inicial': {
            'perspectivas': {
                'sociedade': {'nome': 'Sociedade (Cidadão)', 'objetivos': []},
                'processos': {'nome': 'Processos Internos', 'objetivos': []},
                'aprendizado': {'nome': 'Aprendizado e Crescimento', 'objetivos': []},
                'orcamentaria': {'nome': 'Orçamentária e Financeira', 'objetivos': []}
            },
            'mapa_estrategico': {}
        }
    },
    'okr': {
        'nome': 'Objectives and Key Results',
        'nome_curto': 'OKR',
        'descricao': 'Metodologia ágil de definição de objetivos e resultados-chave. Recomendado pelo MGI.',
        'icone': '🎯',
        'complexidade': 'baixa',
        'prazo': 'curto',
        'maturidade': 'iniciante',
        'tags': ['ágil', 'trimestral', 'foco'],
        'componentes': ['Objetivos', 'Resultados-Chave', 'Iniciativas', 'Check-ins'],
        'vantagens_publico': [
            'Ciclos curtos (trimestrais)',
            'Alinhamento vertical e horizontal',
            'Recomendado no Guia MGI'
        ],
        'quando_usar': [
            'Projetos com entregas rápidas',
            'Equipes que precisam de foco',
            'Transformação digital'
        ],
        'estrutura_inicial': {
            'trimestre': '',
            'objetivos': []
        }
    },
    'swot': {
        'nome': 'Análise SWOT/FOFA',
        'nome_curto': 'SWOT',
        'descricao': 'Diagnóstico situacional através de Forças, Fraquezas, Oportunidades e Ameaças.',
        'icone': '🔍',
        'complexidade': 'baixa',
        'prazo': 'curto',
        'maturidade': 'iniciante',
        'tags': ['diagnóstico', 'simples', 'visual'],
        'componentes': ['Forças', 'Fraquezas', 'Oportunidades', 'Ameaças', 'Matriz Cruzada'],
        'vantagens_publico': [
            'Simplicidade e rapidez',
            'Amplamente conhecido',
            'Base para outros planejamentos'
        ],
        'quando_usar': [
            'Início de gestão',
            'Diagnóstico rápido',
            'Preparação para mudanças'
        ],
        'estrutura_inicial': {
            'forcas': [],
            'fraquezas': [],
            'oportunidades': [],
            'ameacas': [],
            'estrategias_cruzadas': {'fo': [], 'fa': [], 'do': [], 'da': []}
        }
    },
    'cenarios': {
        'nome': 'Planejamento por Cenários',
        'nome_curto': 'Cenários',
        'descricao': 'Construção de futuros possíveis para navegação em ambientes de alta incerteza.',
        'icone': '🔮',
        'complexidade': 'alta',
        'prazo': 'longo',
        'maturidade': 'avancado',
        'tags': ['incerteza', 'futuro', 'estratégico'],
        'componentes': ['Forças Motrizes', 'Incertezas Críticas', 'Cenários', 'Indicadores Antecipados', 'Estratégias Robustas'],
        'vantagens_publico': [
            'Preparação para mudanças políticas',
            'Resiliência organizacional',
            'Usado por IPEA e ENAP'
        ],
        'quando_usar': [
            'Alta incerteza política/orçamentária',
            'Planejamento de longo prazo',
            'Órgãos estratégicos'
        ],
        'estrutura_inicial': {
            'forcas_motrizes': [],
            'incertezas_criticas': [],
            'cenarios': [],
            'estrategias_robustas': []
        }
    },
    '5w2h': {
        'nome': 'Plano de Ação 5W2H',
        'nome_curto': '5W2H',
        'descricao': 'Ferramenta tática para execução rápida: What, Why, Where, When, Who, How, How much.',
        'icone': '⚡',
        'complexidade': 'baixa',
        'prazo': 'curto',
        'maturidade': 'iniciante',
        'tags': ['execução', 'tático', 'rápido'],
        'componentes': ['O quê', 'Por quê', 'Onde', 'Quando', 'Quem', 'Como', 'Quanto'],
        'vantagens_publico': [
            'Execução imediata',
            'Clareza nas responsabilidades',
            'Controle de recursos'
        ],
        'quando_usar': [
            'Projetos específicos',
            'Planos de ação rápidos',
            'Implementação de melhorias'
        ],
        'estrutura_inicial': {
            'acoes': []
        }
    },
    'hoshin': {
        'nome': 'Hoshin Kanri',
        'nome_curto': 'Hoshin Kanri',
        'descricao': 'Metodologia japonesa de desdobramento estratégico em cascata. Para organizações maduras.',
        'icone': '🎌',
        'complexidade': 'alta',
        'prazo': 'longo',
        'maturidade': 'avancado',
        'tags': ['cascata', 'japonês', 'avançado'],
        'componentes': ['Estratégia Breakthrough', 'Matriz X', 'Catchball', 'A3 Reports', 'Bowlers'],
        'vantagens_publico': [
            'Alinhamento total da organização',
            'Melhoria contínua integrada',
            'Gestão visual'
        ],
        'quando_usar': [
            'Alta maturidade em gestão',
            'Cultura de melhoria contínua',
            'Organizações com processos estáveis'
        ],
        'estrutura_inicial': {
            'breakthrough': '',
            'matriz_x': {},
            'catchballs': []
        }
    }
}


# ============================================================================
# PERGUNTAS DO DIAGNÓSTICO
# ============================================================================

PERGUNTAS_DIAGNOSTICO: List[Dict[str, Any]] = [
    {
        'id': 'maturidade',
        'texto': 'Qual o nível de maturidade em planejamento estratégico da sua organização?',
        'opcoes': [
            {
                'valor': 'iniciante',
                'texto': '🌱 Iniciante - Estamos começando agora',
                'pontos': {'swot': 3, '5w2h': 3, 'okr': 2, 'tradicional': 1}
            },
            {
                'valor': 'intermediario',
                'texto': '📈 Intermediário - Já temos alguma experiência',
                'pontos': {'tradicional': 3, 'okr': 2, 'bsc': 1}
            },
            {
                'valor': 'avancado',
                'texto': '🏆 Avançado - Processos maduros e consolidados',
                'pontos': {'bsc': 3, 'cenarios': 3, 'hoshin': 2}
            }
        ]
    },
    {
        'id': 'horizonte',
        'texto': 'Qual o horizonte temporal do seu planejamento?',
        'opcoes': [
            {
                'valor': 'curto',
                'texto': '⚡ Curto prazo (até 1 ano)',
                'pontos': {'5w2h': 3, 'okr': 3, 'swot': 2}
            },
            {
                'valor': 'medio',
                'texto': '📅 Médio prazo (1-2 anos)',
                'pontos': {'okr': 2, 'tradicional': 2, 'bsc': 1}
            },
            {
                'valor': 'longo',
                'texto': '🎯 Longo prazo (3+ anos)',
                'pontos': {'tradicional': 3, 'bsc': 3, 'cenarios': 3, 'hoshin': 2}
            }
        ]
    },
    {
        'id': 'contexto',
        'texto': 'Qual o principal desafio do seu contexto atual?',
        'opcoes': [
            {
                'valor': 'incerteza',
                'texto': '🔄 Mudanças frequentes e incerteza',
                'pontos': {'cenarios': 3, 'okr': 2, '5w2h': 1}
            },
            {
                'valor': 'medicao',
                'texto': '📊 Necessidade de medir resultados',
                'pontos': {'bsc': 3, 'okr': 3, 'tradicional': 1}
            },
            {
                'valor': 'execucao',
                'texto': '🚀 Execução rápida de projetos',
                'pontos': {'5w2h': 3, 'okr': 2}
            },
            {
                'valor': 'conformidade',
                'texto': '🏛️ Conformidade e prestação de contas',
                'pontos': {'tradicional': 3, 'bsc': 2}
            }
        ]
    },
    {
        'id': 'equipe',
        'texto': 'Como você descreveria sua equipe?',
        'opcoes': [
            {
                'valor': 'pequena',
                'texto': '👥 Pequena e ágil (até 20 pessoas)',
                'pontos': {'okr': 3, '5w2h': 2, 'swot': 2}
            },
            {
                'valor': 'media',
                'texto': '🏢 Média com múltiplas áreas (20-100)',
                'pontos': {'tradicional': 2, 'bsc': 2, 'okr': 1}
            },
            {
                'valor': 'grande',
                'texto': '🌐 Grande e complexa (100+)',
                'pontos': {'bsc': 3, 'tradicional': 2, 'hoshin': 2, 'cenarios': 1}
            }
        ]
    },
    {
        'id': 'objetivo',
        'texto': 'Qual o principal objetivo do planejamento?',
        'opcoes': [
            {
                'valor': 'diagnostico',
                'texto': '📋 Diagnosticar a situação atual',
                'pontos': {'swot': 3, 'cenarios': 1}
            },
            {
                'valor': 'estrategia',
                'texto': '🎯 Definir direção estratégica',
                'pontos': {'tradicional': 3, 'bsc': 3, 'cenarios': 2}
            },
            {
                'valor': 'operacional',
                'texto': '⚙️ Operacionalizar projetos',
                'pontos': {'5w2h': 3, 'okr': 3}
            },
            {
                'valor': 'transformacao',
                'texto': '🔄 Transformação organizacional',
                'pontos': {'okr': 2, 'bsc': 2, 'hoshin': 3}
            }
        ]
    }
]
