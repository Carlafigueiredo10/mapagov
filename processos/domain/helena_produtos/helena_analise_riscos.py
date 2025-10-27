# processos/helena_produtos/helena_analise_riscos.py
# =======================================================
# Helena - Análise de Riscos HÍBRIDA
# =======================================================
# VERSÃO 2.0 - Mantém compatibilidade com backend existente
# + Adiciona modo conversacional opcional
# =======================================================

import json
import openai
import logging
from datetime import datetime
import os
import re
import hashlib
from typing import Dict, Any, Optional, Tuple, List

# =========================
# Logging & Config
# =========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("helena_risks")

# =========================
# MODO 1: CONVERSACIONAL (NOVO)
# =========================

class HelenaAnaliseRiscos:
    """
    Classe conversacional para coleta de dados de riscos.
    Uso: Via /api/chat/ com contexto='analise_riscos'
    """

    def __init__(self):
        self.estado = 'inicial'
        self.dados_processo = {}
        self.respostas_brutas = {}
        self.respostas_normalizadas = {}
        self.etapa_atual = 0
        self.conversas = []

        # Fluxo de perguntas organizadas por seções
        self.SECOES = [
            {
                "nome": "Contexto Geral",
                "perguntas": [
                    {
                        "id": "contexto_geral",
                        "tipo": "texto_livre",
                        "mensagem": "Oi! Vamos conversar sobre o processo. Me conta brevemente como ele funciona no dia a dia?",
                        "map_to": "observacoes_adicionais"
                    },
                    {
                        "id": "dependencias_externas",
                        "tipo": "sim_nao",
                        "mensagem": "O processo depende de aprovações ou sistemas de outros órgãos/áreas?",
                        "map_to": "1"  # dependencias_externas_nao_no_pop
                    },
                    {
                        "id": "picos_demanda",
                        "tipo": "sim_nao",
                        "mensagem": "Existem períodos do ano com muito mais demanda que o normal (ex: final do ano, férias)?",
                        "map_to": "2"  # picos_sazonais_demanda
                    }
                ]
            },
            {
                "nome": "Sistemas e Tecnologia",
                "perguntas": [
                    {
                        "id": "conflito_normativo",
                        "tipo": "escala",
                        "mensagem": "Qual o risco de haver conflito entre as normas que regem o processo?",
                        "opcoes": ["Baixo", "Médio", "Alto"],
                        "map_to": "3"  # risco_conflito_normativo
                    },
                    {
                        "id": "apontamentos_controle",
                        "tipo": "sim_nao",
                        "mensagem": "Já houve apontamentos de TCU, CGU ou Ouvidoria sobre este processo?",
                        "map_to": "4"  # apontamentos_tcu_cgu_ouvidoria
                    },
                    {
                        "id": "segregacao_funcoes",
                        "tipo": "sim_nao",
                        "mensagem": "A mesma pessoa que solicita também pode aprovar? (isso seria um problema de segregação)",
                        "map_to": "5",  # segregacao_funcoes_adequada
                        "inverter": True
                    }
                ]
            },
            {
                "nome": "Equipe e Operação",
                "perguntas": [
                    {
                        "id": "backup_operadores",
                        "tipo": "sim_nao",
                        "mensagem": "Se alguém da equipe se ausenta, outra pessoa consegue assumir facilmente as tarefas?",
                        "map_to": "6"  # plano_backup_operadores
                    },
                    {
                        "id": "treinamento",
                        "tipo": "sim_nao",
                        "mensagem": "A equipe recebe treinamento periódico sobre normas e sistemas?",
                        "map_to": "7"  # equipe_treinada_atualizada
                    },
                    {
                        "id": "sistemas_indisponibilidade",
                        "tipo": "escala",
                        "mensagem": "Com que frequência os sistemas (SIGEPE, SEI, SouGov) ficam fora do ar?",
                        "opcoes": ["Nunca", "Raramente (1x/mês)", "Às vezes (1x/semana)", "Frequentemente (>2x/semana)"],
                        "map_to": "8"  # sistemas_risco_indisponibilidade
                    }
                ]
            },
            {
                "nome": "Gestão Documental",
                "perguntas": [
                    {
                        "id": "inconsistencia_dados",
                        "tipo": "sim_nao",
                        "mensagem": "Já houve casos de dados diferentes entre sistemas (ex: CPF no SIAPE ≠ SEI)?",
                        "map_to": "9"  # inconsistencia_dados_sistemas
                    },
                    {
                        "id": "plano_contingencia",
                        "tipo": "sim_nao",
                        "mensagem": "Existe procedimento alternativo quando o sistema cai?",
                        "map_to": "10"  # plano_contingencia_sistemas
                    },
                    {
                        "id": "documentos_devolvidos",
                        "tipo": "sim_nao",
                        "mensagem": "Documentos costumam ser devolvidos para correção?",
                        "map_to": "11"  # documentos_devolvidos_frequentemente
                    },
                    {
                        "id": "taxa_devolucoes",
                        "tipo": "sim_nao",
                        "mensagem": "Mais de 10% dos documentos são devolvidos?",
                        "map_to": "12"  # taxa_devolucoes_supera_10pct
                    }
                ]
            },
            {
                "nome": "Segurança e Integridade",
                "perguntas": [
                    {
                        "id": "fraude",
                        "tipo": "sim_nao",
                        "mensagem": "Já houve caso ou suspeita de fraude/manipulação de documentos?",
                        "map_to": "13"  # risco_fraude_documental
                    },
                    {
                        "id": "gargalos",
                        "tipo": "texto_livre",
                        "mensagem": "Qual etapa do processo costuma atrasar mais?",
                        "map_to": "14"  # gargalos_principais_fluxo
                    },
                    {
                        "id": "tempo_medio",
                        "tipo": "numero",
                        "mensagem": "Qual o tempo médio para concluir um processo? (em dias)",
                        "map_to": "15"  # tempo_medio_conclusao_dias
                    }
                ]
            },
            {
                "nome": "Riscos Financeiros",
                "perguntas": [
                    {
                        "id": "calculo_incorreto",
                        "tipo": "sim_nao",
                        "mensagem": "Já houve erro de cálculo que gerou pagamento incorreto?",
                        "map_to": "16"  # risco_calculo_incorreto
                    },
                    {
                        "id": "reposicao_erario",
                        "tipo": "sim_nao",
                        "mensagem": "Já foi necessário devolver dinheiro ao erário por erro?",
                        "map_to": "17"  # reposicao_erario_anterior
                    }
                ]
            },
            {
                "nome": "Conformidade e LGPD",
                "perguntas": [
                    {
                        "id": "dados_sensiveis",
                        "tipo": "sim_nao",
                        "mensagem": "O processo trata dados pessoais sensíveis (CPF, saúde, financeiros)?",
                        "map_to": "18"  # dados_pessoais_sensiveis_lgpd
                    },
                    {
                        "id": "controles_internos",
                        "tipo": "sim_nao",
                        "mensagem": "Existem controles formalizados (checklist, dupla conferência, indicadores)?",
                        "map_to": "19"  # controles_internos_existentes
                    }
                ]
            }
        ]

        # Total de perguntas
        self.total_perguntas = sum(len(secao["perguntas"]) for secao in self.SECOES)
        self.pergunta_atual_idx = 0
        self.secao_atual_idx = 0

    def processar_mensagem(self, mensagem: str) -> Dict[str, Any]:
        """Processa mensagem do usuário no fluxo conversacional"""

        # Estado inicial - apresentação
        if self.estado == 'inicial':
            self.estado = 'coletando_dados'
            return self._proxima_pergunta()

        # Coletando dados - processa resposta e faz próxima pergunta
        elif self.estado == 'coletando_dados':
            # Salva resposta anterior
            if self.pergunta_atual_idx > 0:
                self._salvar_resposta(mensagem)

            # Verifica se terminou
            if self.pergunta_atual_idx >= self.total_perguntas:
                self.estado = 'finalizado'
                return self._gerar_relatorio()

            # Próxima pergunta
            return self._proxima_pergunta()

        # Finalizado - gera relatório
        elif self.estado == 'finalizado':
            return {
                'resposta': 'Análise de riscos já foi gerada! Deseja refazer?',
                'dados_extraidos': self.respostas_normalizadas,
                'conversa_completa': True
            }

    def _proxima_pergunta(self) -> Dict[str, Any]:
        """Retorna próxima pergunta do fluxo"""

        # Encontra pergunta atual
        contador = 0
        for secao in self.SECOES:
            for pergunta in secao["perguntas"]:
                if contador == self.pergunta_atual_idx:
                    self.pergunta_atual_idx += 1

                    # Monta resposta com opções se for escala
                    mensagem = pergunta["mensagem"]
                    if pergunta["tipo"] == "escala":
                        opcoes_texto = " | ".join([f"({i+1}) {opt}" for i, opt in enumerate(pergunta["opcoes"])])
                        mensagem += f"\n\n{opcoes_texto}"

                    progresso = f"[{self.pergunta_atual_idx}/{self.total_perguntas}]"

                    return {
                        'resposta': f"{progresso} {mensagem}",
                        'dados_extraidos': self.respostas_normalizadas,
                        'conversa_completa': False,
                        'progresso': {
                            'atual': self.pergunta_atual_idx,
                            'total': self.total_perguntas,
                            'percentual': int((self.pergunta_atual_idx / self.total_perguntas) * 100)
                        }
                    }
                contador += 1

        # Acabaram as perguntas
        self.estado = 'finalizado'
        return self._gerar_relatorio()

    def _salvar_resposta(self, mensagem: str):
        """Salva e normaliza resposta do usuário"""

        # Encontra pergunta anterior
        contador = 0
        for secao in self.SECOES:
            for pergunta in secao["perguntas"]:
                if contador == self.pergunta_atual_idx - 1:
                    pergunta_id = pergunta["id"]
                    map_to = pergunta["map_to"]

                    # Salva bruta
                    self.respostas_brutas[pergunta_id] = mensagem

                    # Normaliza conforme tipo
                    if pergunta["tipo"] == "sim_nao":
                        valor = "sim" if any(x in mensagem.lower() for x in ["sim", "s", "yes", "1"]) else "não"
                        if pergunta.get("inverter"):
                            valor = "não" if valor == "sim" else "sim"
                        self.respostas_normalizadas[map_to] = valor

                    elif pergunta["tipo"] == "escala":
                        # Tenta extrair número ou texto da opção
                        for i, opcao in enumerate(pergunta["opcoes"]):
                            if str(i+1) in mensagem or opcao.lower() in mensagem.lower():
                                self.respostas_normalizadas[map_to] = opcao.lower()
                                break
                        else:
                            self.respostas_normalizadas[map_to] = mensagem.lower()

                    elif pergunta["tipo"] in ["texto_livre", "numero"]:
                        self.respostas_normalizadas[map_to] = mensagem

                    return
                contador += 1

    def _gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório final usando função analyze_risks_helena()"""

        # Chama função de análise existente
        resultado = analyze_risks_helena(
            pop_text=self.dados_processo.get('pop_text', ''),
            pop_info=self.dados_processo.get('pop_info', {}),
            answers=self.respostas_normalizadas,
            model="gpt-4o",
            temperature=0.2,
            max_tokens=7000
        )

        return {
            'resposta': '✅ Análise de riscos concluída! Relatório gerado com sucesso.',
            'dados_extraidos': resultado.get('data', {}),
            'conversa_completa': True,
            'relatorio': resultado
        }


# =========================
# MODO 2: ANÁLISE DIRETA (EXISTENTE)
# =========================
# Mantém toda a implementação original para compatibilidade

HELENA_RISK_ANALYSIS_PROMPT = """
Você é Helena, assistente especializada em Governança, Riscos e Controles (GRC),
baseada nos referenciais COSO ERM (2017), ISO 31000 (2018), Modelo das Três Linhas (IIA, 2020),
Referencial Básico de Governança do TCU e guias da CGU/MGI.

Sua tarefa é elaborar um **Relatório de Análise de Riscos Avançado** para um Procedimento Operacional Padrão (POP).

### O que você receberá como insumo:
1. **Texto integral do POP** (extraído de arquivo PDF) - contém estrutura completa do processo
2. **Respostas ao Questionário de 20 perguntas otimizadas** - complementam aspectos não cobertos pelo POP

### Estrutura JSON de saída AVANÇADA:
{
  "cabecalho": {
    "titulo": "Relatório de Análise de Riscos",
    "pop": "extrair do POP",
    "codigo": "extrair do POP",
    "macroprocesso": "extrair do POP",
    "processo": "extrair do POP",
    "subprocesso": "extrair do POP",
    "atividade": "extrair do POP",
    "responsavel": "extrair do POP ou inferir",
    "data_analise": "formato dd/mm/aaaa"
  },
  "mapa_contexto": {
    "resumo_processo": "síntese do processo em 2-3 frases",
    "partes_interessadas": ["operadores do POP + das respostas"],
    "sistemas_utilizados": ["sistemas do POP + mencionados nas respostas"],
    "documentos_principais": ["documentos do POP + das respostas"],
    "normativos_aplicaveis": ["normativos do POP + das respostas"],
    "pontos_atencao": ["riscos potenciais identificados preliminarmente"]
  },
  "riscos": [
    {
      "titulo": "nome específico do risco",
      "descricao": "descrição contextualizada baseada no POP específico",
      "categoria": "Operacional|Tecnológico|Normativo|Financeiro|Reputacional|Integridade",
      "tipo_risco": "Inerente|Residual",
      "probabilidade": "Baixa|Média|Alta",
      "impacto": "Baixo|Médio|Alto",
      "severidade": "Baixo|Moderado|Alto|Crítico (calculado pela matriz)",
      "apetite_status": "Dentro do apetite|Fora do apetite|Não informado",
      "normativo_relacionado": "citar lei/IN/artigo específico se aplicável",
      "controles_existentes": ["controles mencionados no POP + respostas"],
      "tratamento_recomendado": "sugestão prática e específica",
      "indicadores_monitoramento": ["KPIs sugeridos para acompanhar este risco"],
      "interdependencias": ["IDs ou títulos de riscos relacionados"]
    }
  ],
  "matriz_riscos": {
    "criticos": "contagem",
    "altos": "contagem",
    "moderados": "contagem",
    "baixos": "contagem"
  },
  "plano_tratamento": {
    "mitigacao_imediata": ["ações prioritárias"],
    "monitoramento": ["aspectos a acompanhar"],
    "lacunas_controle": ["controles ausentes"],
    "sugestoes_indicadores": ["KPIs"],
    "interdependencias_criticas": ["relações entre riscos"]
  },
  "sumario_executivo": {
    "maiores_riscos": ["3-5 riscos mais críticos"],
    "areas_criticas": ["áreas vulneráveis"],
    "acoes_urgentes": ["ações imediatas"],
    "sintese_gerencial": "resumo executivo"
  },
  "conclusoes_recomendacoes": "síntese detalhada"
}

**IMPORTANTE**: Retorne APENAS o JSON, sem texto adicional, comentários ou formatação Markdown.
"""

def _strip_accents(s: str) -> str:
    try:
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    except Exception:
        return s

def normalize_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza respostas do questionário para análise consistente."""
    if not answers:
        return {}

    normalized = {}
    boolean_mappings = {
        'sim': ['sim', 's', 'yes', 'y', '1', 'true', 'verdadeiro'],
        'não': ['não', 'nao', 'n', 'no', '0', 'false', 'falso'],
        'não sei': ['não sei', 'nao sei', 'ns', 'desconheço', 'desconheco']
    }

    for q_id, raw_answer in answers.items():
        if raw_answer is None or str(raw_answer).strip() == '':
            normalized[str(q_id)] = 'não informado'
            continue

        text = str(raw_answer).strip()
        low = _strip_accents(text.lower())

        for standard, variants in boolean_mappings.items():
            if low in [_strip_accents(v) for v in variants]:
                normalized[str(q_id)] = standard
                break
        else:
            normalized[str(q_id)] = text

    logger.info(f"[normalize_answers] {len(normalized)} respostas normalizadas")
    return normalized

def analyze_risks_helena(
    pop_text: str,
    pop_info: Dict[str, Any],
    answers: Dict[str, Any],
    model: str = "gpt-4o",
    secondary_model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 7000,
    save_logs: bool = True
) -> Dict[str, Any]:
    """
    Analisa riscos usando Helena especializada em GRC.
    FUNÇÃO PRINCIPAL - Mantida para compatibilidade com views.py
    """
    try:
        normalized_answers = normalize_answers(answers)

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada")

        client = openai.OpenAI(api_key=api_key)

        # Prepara contexto
        context = f"""
=== DADOS DO POP ===
Título: {pop_info.get('titulo', 'Não identificado')}
Código: {pop_info.get('codigo', 'N/A')}

Conteúdo:
{pop_text[:9000]}

=== RESPOSTAS ===
{json.dumps(normalized_answers, indent=2, ensure_ascii=False)}

Retorne análise de riscos em JSON conforme especificado.
"""

        # Chama GPT-4
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": HELENA_RISK_ANALYSIS_PROMPT},
                {"role": "user", "content": context}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content.strip()
        final_report = json.loads(raw)

        logger.info(f"[analyze_risks_helena] Sucesso | riscos={len(final_report.get('riscos', []))}")
        return {'success': True, 'data': final_report}

    except Exception as e:
        logger.error(f"[analyze_risks_helena] Erro: {e}")
        return {
            'success': False,
            'error': str(e),
            'data': {
                'cabecalho': {'titulo': 'Erro na análise'},
                'riscos': [],
                'conclusoes_recomendacoes': f'Erro: {str(e)}'
            }
        }


# =========================
# Execução direta (teste)
# =========================
if __name__ == "__main__":
    print("=== TESTE: Modo Conversacional ===")
    helena = HelenaAnaliseRiscos()

    # Simula conversa
    mensagens_teste = [
        "Processo de aposentadoria, análise de documentos",
        "sim",  # dependências externas
        "não",  # picos demanda
        "médio",  # conflito normativo
        # ... etc
    ]

    for msg in mensagens_teste[:3]:
        resultado = helena.processar_mensagem(msg)
        print(f"\nHelena: {resultado['resposta']}")
        print(f"Progresso: {resultado.get('progresso', {})}")
