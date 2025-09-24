# processos/helena_risks.py
# Helena especializada em análise de riscos - VERSÃO OTIMIZADA, CORRIGIDA E COM MODELO DINÂMICO

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
# Prompt principal
# =========================
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
  "analise_categorias": {
    "operacional": "contagem",
    "tecnologico": "contagem",
    "normativo": "contagem",
    "financeiro": "contagem",
    "reputacional": "contagem",
    "integridade": "contagem"
  },
  "plano_tratamento": {
    "mitigacao_imediata": ["ações prioritárias baseadas nos riscos críticos/altos"],
    "monitoramento": ["aspectos que devem ser acompanhados"],
    "lacunas_controle": ["controles ausentes identificados"],
    "sugestoes_indicadores": ["KPIs para monitorar os riscos"],
    "interdependencias_criticas": ["relações entre riscos que amplificam impacto"]
  },
  "sumario_executivo": {
    "maiores_riscos": ["3-5 riscos mais críticos"],
    "areas_criticas": ["áreas do processo mais vulneráveis"],
    "acoes_urgentes": ["ações que requerem atenção imediata"],
    "sintese_gerencial": "resumo de 3-5 frases para tomada de decisão"
  },
  "conclusoes_recomendacoes": "síntese executiva detalhada para gestores"
}

### Matriz de Severidade (Probabilidade × Impacto):
- Baixa + Baixo = Baixo
- Baixa + Médio = Baixo
- Baixa + Alto = Moderado
- Média + Baixo = Baixo
- Média + Médio = Moderado
- Média + Alto = Alto
- Alta + Baixo = Moderado
- Alta + Médio = Alto
- Alta + Alto = Crítico

### Diretrizes específicas AVANÇADAS:
1. **Contextualização obrigatória**: Riscos devem ser específicos do processo analisado, nunca genéricos
2. **Uso de dados reais**: Baseie-se exclusivamente no POP fornecido + respostas
3. **Quantidade**: Identifique 6-10 riscos relevantes (mínimo 6, máximo 10)
4. **Categorização rigorosa**: Use EXATAMENTE uma das 6 categorias (Operacional, Tecnológico, Normativo, Financeiro, Reputacional, Integridade)
5. **Severidade calculada**: Use automaticamente a matriz probabilidade × impacto
6. **Tratamentos práticos**: Sejam específicos e implementáveis no contexto do POP
7. **Rastreabilidade normativa**: Para riscos normativos, cite explicitamente artigos/INs/leis do POP
8. **Risco inerente vs residual**: Classifique se o risco é antes ou depois dos controles existentes
9. **Apetite de risco**: Use "Não informado" quando política institucional não estiver clara
10. **Indicadores específicos**: Sugira KPIs derivados do processo específico
11. **Interdependências**: Identifique relações entre riscos (causa-efeito)
12. **Sumário executivo**: Destaque maiores riscos, áreas críticas, ações urgentes

**IMPORTANTE**: Retorne APENAS o JSON, sem texto adicional, comentários ou formatação Markdown.
"""

# =========================
# Normalização & utilitários
# =========================

def _strip_accents(s: str) -> str:
    try:
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    except Exception:
        return s

def normalize_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza respostas do questionário para análise consistente.
    """
    if not answers:
        return {}

    normalized = {}

    boolean_mappings = {
        'sim': ['sim', 's', 'yes', 'y', '1', 'true', 'verdadeiro'],
        'não': ['não', 'nao', 'n', 'no', '0', 'false', 'falso'],
        'não sei': ['não sei', 'nao sei', 'ns', 'desconheço', 'desconheco', 'não informado', 'nao informado']
    }

    risk_level_mappings = {
        'baixo': ['baixo', 'baixa', 'low', 'pequeno', 'reduzido'],
        'médio': ['médio', 'media', 'medio', 'medium', 'moderado', 'intermediario'],
        'alto':  ['alto', 'alta', 'high', 'elevado', 'grande', 'significativo']
    }

    for q_id, raw_answer in answers.items():
        if raw_answer is None or str(raw_answer).strip() == '':
            normalized[str(q_id)] = 'não informado'
            continue

        text = str(raw_answer).strip()
        low = _strip_accents(text.lower())

        # boolean
        for standard, variants in boolean_mappings.items():
            if low in [_strip_accents(v) for v in variants]:
                normalized[str(q_id)] = standard
                break
        else:
            # níveis
            matched = False
            for standard, variants in risk_level_mappings.items():
                for v in variants:
                    if _strip_accents(v) in low:
                        normalized[str(q_id)] = standard
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                normalized[str(q_id)] = text  # mantém original

    logger.info(f"[normalize_answers] {len(normalized)} respostas normalizadas")
    return normalized

def validate_question_mapping() -> Dict[int, str]:
    """
    Mapeamento corrigido para exatamente 20 perguntas (1..20).
    """
    corrected_question_map = {
        1: "dependencias_externas_nao_no_pop",
        2: "picos_sazonais_demanda",
        3: "risco_conflito_normativo",
        4: "apontamentos_tcu_cgu_ouvidoria",
        5: "segregacao_funcoes_adequada",
        6: "plano_backup_operadores",
        7: "equipe_treinada_atualizada",
        8: "sistemas_risco_indisponibilidade",
        9: "inconsistencia_dados_sistemas",
        10: "plano_contingencia_sistemas",
        11: "documentos_devolvidos_frequentemente",
        12: "taxa_devolucoes_supera_10pct",
        13: "risco_fraude_documental",
        14: "gargalos_principais_fluxo",
        15: "tempo_medio_conclusao_dias",
        16: "risco_calculo_incorreto",
        17: "reposicao_erario_anterior",
        18: "dados_pessoais_sensiveis_lgpd",
        19: "controles_internos_existentes",
        20: "observacoes_adicionais"
    }
    expected = set(range(1, 21))
    got = set(corrected_question_map.keys())
    if expected != got:
        logger.warning(f"[validate_question_mapping] diff: missing={expected - got}, extra={got - expected}")
    return corrected_question_map

# =========================
# Core de análise
# =========================

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
    Analisa riscos usando Helena especializada em GRC com suporte a modelo dinâmico e redundância opcional.
    """
    try:
        normalized_answers = normalize_answers(answers)
        context = prepare_optimized_context(pop_text, pop_info, normalized_answers)

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada")

        client = openai.OpenAI(api_key=api_key)

        primary_json, raw_primary = _call_helena_model(
            client, context, model, temperature=temperature, max_tokens=max_tokens
        )

        final_report = None
        chosen_model = model

        if secondary_model:
            secondary_json, raw_secondary = _call_helena_model(
                client, context, secondary_model, temperature=temperature, max_tokens=max_tokens
            )
            final_report, chosen_model = _reconcile_reports(primary_json, secondary_json, model, secondary_model)
            combined_raw = (raw_primary or "")[:500] + "\n---\n" + (raw_secondary or "")[:500]
        else:
            final_report = primary_json
            combined_raw = (raw_primary or "")[:1000]

        if not final_report:
            logger.warning("[analyze_risks_helena] Usando fallback contextualizado (IA não retornou JSON válido)")
            return generate_fallback_report(pop_info, normalized_answers)

        # Validações & correções
        validate_optimized_report(final_report)
        complete_missing_fields(final_report, pop_info)
        recalculate_risk_matrix(final_report)
        _enforce_min_controls_and_indicators(final_report)  # garante 1 indicador + 1 tratamento
        cross_validate_report(final_report)

        if save_logs:
            save_analysis_log(combined_raw, final_report, success=True)

        logger.info(f"[analyze_risks_helena] Sucesso com modelo: {chosen_model} | riscos={len(final_report.get('riscos', []))}")
        return {'success': True, 'data': final_report}

    except Exception as e:
        logger.error(f"[analyze_risks_helena] Erro: {e}")
        return generate_fallback_report(pop_info, normalize_answers(answers))

def _call_helena_model(client, context: str, model: str, temperature: float, max_tokens: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Chama o modelo especificado e tenta parsear JSON de forma robusta.
    """
    logger.info(f"[_call_helena_model] Chamando modelo: {model}")
    try:
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
        raw = response.choices[0].message.content.strip() if response and response.choices else ""
        logger.info(f"[_call_helena_model] Resposta recebida ({len(raw)} chars)")
        parsed = parse_helena_response(raw)
        return parsed, raw
    except Exception as e:
        logger.error(f"[_call_helena_model] Falha no modelo {model}: {e}")
        return None, None

def _reconcile_reports(r1: Optional[Dict[str, Any]], r2: Optional[Dict[str, Any]], m1: str, m2: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Estratégia simples: escolhe o relatório com mais riscos válidos. Em empate, prefere r1.
    """
    n1 = len(r1.get('riscos', [])) if isinstance(r1, dict) else 0
    n2 = len(r2.get('riscos', [])) if isinstance(r2, dict) else 0

    if n1 >= n2 and r1:
        return r1, m1
    if r2:
        return r2, m2
    return r1 or r2, m1 if r1 else m2

# =========================
# Parsing & contexto
# =========================

def parse_helena_response(helena_response: str) -> Optional[Dict[str, Any]]:
    """
    Parse robusto da resposta, lidando com formatos diversos.
    """
    if not helena_response:
        return None

    # 1) Direto
    try:
        return json.loads(helena_response)
    except json.JSONDecodeError:
        pass

    # 2) Bloco ```json
    block = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", helena_response)
    if block:
        txt = block.group(1)
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            pass

    # 3) Maior objeto entre chaves
    cleaned = _sanitize_trailing_commas(helena_response)
    match = _largest_curly_json(cleaned)
    if match:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            pass

    # 4) Tentativa de capturar primeira chave bem formada
    start = helena_response.find('{')
    end = helena_response.rfind('}') + 1
    if start != -1 and end != -1 and end > start:
        snippet = helena_response[start:end]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            pass

    logger.error("[parse_helena_response] Não foi possível parsear JSON")
    return None

def _sanitize_trailing_commas(text: str) -> str:
    """
    Remove vírgulas finais comuns em JSONs gerados por LLM.
    """
    text = re.sub(r",\s*([\}\]])", r"\1", text)
    return text

def _largest_curly_json(text: str) -> Optional[str]:
    """
    Retorna o maior bloco que começa com '{' e termina com '}' balanceado.
    """
    stack = []
    start_idx = None
    best = None
    for i, ch in enumerate(text):
        if ch == '{':
            if not stack:
                start_idx = i
            stack.append('{')
        elif ch == '}':
            if stack:
                stack.pop()
                if not stack and start_idx is not None:
                    candidate = text[start_idx:i+1]
                    if not best or len(candidate) > len(best):
                        best = candidate
    return best

def prepare_optimized_context(pop_text: str, pop_info: Dict[str, Any], normalized_answers: Dict[str, Any]) -> str:
    """
    Prepara contexto com truncamento controlado e mapeamento 1..20.
    """
    question_map = validate_question_mapping()

    structured_answers = {}
    for q_id, answer in normalized_answers.items():
        if str(q_id).isdigit() and int(q_id) in question_map:
            structured_answers[question_map[int(q_id)]] = answer
        else:
            structured_answers[f"pergunta_{q_id}"] = answer

    max_pop_chars = 9000  # margem para mensagens e instruções
    pop_content = pop_text[:max_pop_chars]
    truncated = len(pop_text) > max_pop_chars

    if truncated:
        pop_content += "\n...\n[CONTEÚDO TRUNCADO - POP MUITO EXTENSO]"
        logger.warning(f"[prepare_optimized_context] POP truncado de {len(pop_text)} para {max_pop_chars} caracteres")

    normativos = pop_info.get('normativos', [])
    normativos_hint = '; '.join(normativos[:5]) if normativos else 'Não especificados'

    context = f"""
=== DADOS DO POP EXTRAÍDO ===

**Identificação:**
- Título: {pop_info.get('titulo', 'Não identificado')}
- Código: {pop_info.get('codigo', 'N/A')}
- Macroprocesso: {pop_info.get('macroprocesso', 'N/A')}
- Processo: {pop_info.get('processo', 'N/A')}
- Subprocesso: {pop_info.get('subprocesso', 'N/A')}
- Atividade: {pop_info.get('atividade', 'N/A')}
- Responsável: {pop_info.get('responsavel', 'N/A')}

**Elementos identificados no POP:**
- Sistemas utilizados: {', '.join(pop_info.get('sistemas', ['Nenhum identificado']))}
- Operadores/perfis: {', '.join(pop_info.get('operadores', ['Não especificados']))}
- Normativos aplicáveis: {normativos_hint}

**Conteúdo do POP:**
{pop_content}

=== RESPOSTAS DO QUESTIONÁRIO (NORMALIZADAS) ===
{json.dumps(structured_answers, indent=2, ensure_ascii=False)}

=== INSTRUÇÕES PARA ANÁLISE ===
1. Cruze informações do POP com respostas do questionário normalizado
2. Identifique 6-10 riscos específicos deste processo (não genéricos)
3. Use EXATAMENTE as categorias: Operacional, Tecnológico, Normativo, Financeiro, Reputacional, Integridade
4. Para apetite de risco, use "Não informado" quando não houver política clara
5. Calcule severidade rigorosamente usando matriz probabilidade × impacto
6. Sugira tratamentos práticos e implementáveis
7. Para normativos, cite especificamente os do POP: {normativos_hint}

Retorne apenas o JSON estruturado conforme especificado.
"""
    return context

# =========================
# Validação & correções
# =========================

def validate_optimized_report(report: Dict[str, Any]) -> None:
    """
    Validação avançada e correções pontuais.
    """
    required_keys = ['cabecalho', 'mapa_contexto', 'riscos', 'matriz_riscos', 'plano_tratamento', 'sumario_executivo']
    missing = [k for k in required_keys if k not in report]
    if missing:
        logger.error(f"[validate_optimized_report] Faltam chaves: {missing}")
        raise ValueError(f"Chaves obrigatórias ausentes: {', '.join(missing)}")

    # Cabeçalho mínimo
    for k in ['titulo', 'pop', 'data_analise']:
        if k not in report['cabecalho']:
            logger.warning(f"[validate_optimized_report] Cabeçalho incompleto, faltando '{k}'")

    riscos = report.get('riscos', [])
    if not isinstance(riscos, list) or len(riscos) < 3:
        raise ValueError("Relatório deve conter pelo menos 3 riscos identificados")

    valid_categories = ['Operacional', 'Tecnológico', 'Normativo', 'Financeiro', 'Reputacional', 'Integridade']
    valid_risk_types = ['Inerente', 'Residual']
    valid_prob = ['Baixa', 'Média', 'Alta']
    valid_imp = ['Baixo', 'Médio', 'Alto']
    valid_sev = ['Baixo', 'Moderado', 'Alto', 'Crítico']

    for i, r in enumerate(riscos):
        needed = ['titulo', 'descricao', 'categoria', 'tipo_risco', 'probabilidade', 'impacto', 'severidade']
        miss = [k for k in needed if k not in r]
        if miss:
            raise ValueError(f"Risco {i+1} incompleto: falta {', '.join(miss)}")

        # Corrigir categoria comuns erroneas
        cat = r.get('categoria', 'Operacional')
        if cat == 'Legal':
            cat = 'Normativo'
        mapping = {
            'Regulatório': 'Normativo',
            'Compliance': 'Normativo',
            'Sistêmico': 'Tecnológico',
            'Processual': 'Operacional'
        }
        r['categoria'] = mapping.get(cat, cat)
        if r['categoria'] not in valid_categories:
            logger.warning(f"[validate_optimized_report] Categoria inválida '{r['categoria']}', usando 'Operacional'")
            r['categoria'] = 'Operacional'

        # Padronizar prob/impact
        r['probabilidade'] = str(r['probabilidade']).strip().capitalize()
        r['impacto'] = str(r['impacto']).strip().capitalize()

        if r['probabilidade'] not in valid_prob:
            r['probabilidade'] = 'Média'
        if r['impacto'] not in valid_imp:
            r['impacto'] = 'Médio'

        if r.get('tipo_risco') not in valid_risk_types:
            r['tipo_risco'] = 'Inerente'

        # Recalcular severidade
        calc = calculate_severity(r['probabilidade'], r['impacto'])
        if r.get('severidade') not in valid_sev or r['severidade'] != calc:
            logger.warning(f"[validate_optimized_report] Severidade ajustada: {r.get('severidade')} -> {calc}")
            r['severidade'] = calc

def calculate_severity(probabilidade: str, impacto: str) -> str:
    matriz = {
        ('Baixa', 'Baixo'): 'Baixo',
        ('Baixa', 'Médio'): 'Baixo',
        ('Baixa', 'Alto'): 'Moderado',
        ('Média', 'Baixo'): 'Baixo',
        ('Média', 'Médio'): 'Moderado',
        ('Média', 'Alto'): 'Alto',
        ('Alta', 'Baixo'): 'Moderado',
        ('Alta', 'Médio'): 'Alto',
        ('Alta', 'Alto'): 'Crítico'
    }
    return matriz.get((probabilidade, impacto), 'Moderado')

def complete_missing_fields(report: Dict[str, Any], pop_info: Dict[str, Any]) -> None:
    cab = report.get('cabecalho', {})
    if not cab.get('data_analise') or cab['data_analise'] in ['dd/mm/aaaa', '']:
        cab['data_analise'] = datetime.now().strftime('%d/%m/%Y')

    defaults = {
        'titulo': 'Relatório de Análise de Riscos',
        'pop': pop_info.get('titulo', 'Processo não identificado'),
        'codigo': pop_info.get('codigo', 'N/A'),
        'macroprocesso': pop_info.get('macroprocesso', 'N/A'),
        'processo': pop_info.get('processo', 'N/A'),
        'subprocesso': pop_info.get('subprocesso', 'N/A'),
        'atividade': pop_info.get('atividade', 'N/A'),
        'responsavel': pop_info.get('responsavel', 'A definir')
    }
    for k, v in defaults.items():
        if not cab.get(k):
            cab[k] = v

    for r in report.get('riscos', []):
        if not r.get('tratamento_recomendado'):
            r['tratamento_recomendado'] = 'Definir tratamento específico com base no contexto do POP'
        if not r.get('controles_existentes'):
            r['controles_existentes'] = ['A definir']
        if not r.get('apetite_status'):
            r['apetite_status'] = 'Não informado'
        if not r.get('normativo_relacionado'):
            r['normativo_relacionado'] = 'A especificar' if r.get('categoria') == 'Normativo' else 'Não aplicável'
        if not r.get('indicadores_monitoramento'):
            r['indicadores_monitoramento'] = ['A definir']
        if not r.get('interdependencias'):
            r['interdependencias'] = []

    if 'analise_categorias' not in report:
        report['analise_categorias'] = calculate_category_analysis(report.get('riscos', []))
    if 'sumario_executivo' not in report:
        report['sumario_executivo'] = generate_executive_summary(report.get('riscos', []))
    if not report.get('conclusoes_recomendacoes'):
        report['conclusoes_recomendacoes'] = generate_conclusions(report.get('riscos', []))

def _enforce_min_controls_and_indicators(report: Dict[str, Any]) -> None:
    """
    Garante pelo menos 1 indicador e 1 tratamento por risco.
    """
    for r in report.get('riscos', []):
        if not r.get('tratamento_recomendado') or r['tratamento_recomendado'].strip() == '':
            r['tratamento_recomendado'] = 'Definir tratamento específico com base no contexto do POP'
        if not r.get('indicadores_monitoramento') or not isinstance(r['indicadores_monitoramento'], list) or len(r['indicadores_monitoramento']) == 0:
            r['indicadores_monitoramento'] = ['A definir']

def calculate_category_analysis(risks: List[Dict[str, Any]]) -> Dict[str, int]:
    categories = {
        'operacional': 0,
        'tecnologico': 0,
        'normativo': 0,
        'financeiro': 0,
        'reputacional': 0,
        'integridade': 0
    }
    mapping = {
        'operacional': ['operacional'],
        'tecnologico': ['tecnológico', 'tecnologico'],
        'normativo': ['normativo'],
        'financeiro': ['financeiro'],
        'reputacional': ['reputacional'],
        'integridade': ['integridade']
    }
    for r in risks:
        cat = str(r.get('categoria', '')).lower()
        placed = False
        for key, vars_ in mapping.items():
            if any(v in cat for v in vars_):
                categories[key] += 1
                placed = True
                break
        if not placed:
            categories['operacional'] += 1
    return categories

def generate_executive_summary(risks: List[Dict[str, Any]]) -> Dict[str, Any]:
    high = [r['titulo'] for r in risks if r.get('severidade') in ['Crítico', 'Alto']]
    counts = {}
    for r in risks:
        c = r.get('categoria', 'Operacional')
        counts[c] = counts.get(c, 0) + 1
    areas = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
    urgent = []
    for r in risks:
        if r.get('severidade') == 'Crítico' and r.get('tratamento_recomendado'):
            urgent.append(f"Mitigar: {r['titulo']}")
    if len(urgent) < 2:
        urgent.extend(["Implementar controles para riscos altos", "Estabelecer monitoramento dos indicadores"])
    return {
        'maiores_riscos': high[:5] if high else [r['titulo'] for r in risks[:3]],
        'areas_criticas': [a[0] for a in areas],
        'acoes_urgentes': urgent[:5],
        'sintese_gerencial': f"Processo apresenta {len(risks)} riscos identificados, com {len(high)} classificados como críticos/altos. Áreas com maior exposição: {', '.join([a[0] for a in areas[:2]])}. Ações imediatas recomendadas para mitigar as exposições mais significativas."
    }

def generate_conclusions(risks: List[Dict[str, Any]]) -> str:
    crit = len([r for r in risks if r.get('severidade') == 'Crítico'])
    high = len([r for r in risks if r.get('severidade') == 'Alto'])
    if crit > 0:
        prio, action = "crítica", "ações imediatas são necessárias"
    elif high > 2:
        prio, action = "alta", "medidas corretivas devem ser priorizadas"
    else:
        prio, action = "moderada", "melhorias incrementais são recomendadas"
    return f"Análise identificou {len(risks)} riscos, sendo {crit} críticos e {high} altos. Exposição geral {prio}; {action.capitalize()} para assegurar governança e conformidade."

def recalculate_risk_matrix(report: Dict[str, Any]) -> None:
    counts = {'criticos': 0, 'altos': 0, 'moderados': 0, 'baixos': 0}
    for r in report.get('riscos', []):
        sev = str(r.get('severidade', '')).lower()
        if sev == 'crítico':
            counts['criticos'] += 1
        elif sev == 'alto':
            counts['altos'] += 1
        elif sev == 'moderado':
            counts['moderados'] += 1
        elif sev in ['baixo', 'baixa']:
            counts['baixos'] += 1
        else:
            counts['moderados'] += 1
    report['matriz_riscos'] = counts
    logger.info(f"[recalculate_risk_matrix] {counts}")

def cross_validate_report(report: Dict[str, Any]) -> None:
    actual = {'criticos': 0, 'altos': 0, 'moderados': 0, 'baixos': 0}
    for r in report.get('riscos', []):
        sev = str(r.get('severidade', '')).lower()
        if sev == 'crítico':
            actual['criticos'] += 1
        elif sev == 'alto':
            actual['altos'] += 1
        elif sev == 'moderado':
            actual['moderados'] += 1
        else:
            actual['baixos'] += 1
    declared = report.get('matriz_riscos', {})
    diffs = []
    for k in actual:
        if actual.get(k, 0) != declared.get(k, 0):
            diffs.append(f"{k}: real={actual.get(k,0)}, declarado={declared.get(k,0)}")
    if diffs:
        logger.warning(f"[cross_validate_report] Discrepâncias: {', '.join(diffs)} — corrigindo")
        report['matriz_riscos'] = actual

# =========================
# Extração e fallback
# =========================

def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    if not response_text:
        return None
    # Sanear vírgulas finais e blocos
    text = _sanitize_trailing_commas(response_text)
    # Bloco json
    m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Maior objeto
    big = _largest_curly_json(text)
    if big:
        try:
            return json.loads(big)
        except json.JSONDecodeError:
            pass
    # Primeiras chaves
    s, e = text.find('{'), text.rfind('}') + 1
    if s != -1 and e != -1 and e > s:
        try:
            return json.loads(text[s:e])
        except json.JSONDecodeError:
            pass
    logger.error("[extract_json_from_response] Falha ao extrair JSON")
    return None

def generate_fallback_report(pop_info: Dict[str, Any], normalized_answers: Dict[str, Any]) -> Dict[str, Any]:
    logger.warning("[generate_fallback_report] Gerando fallback contextualizado")
    risks = infer_contextual_risks_from_answers(pop_info, normalized_answers)
    # Garante 6 a 8 riscos no fallback
    if len(risks) < 6:
        risks = _pad_min_risks(risks, pop_info)
    matriz = calculate_risk_matrix_from_risks(risks)
    data = {
        'cabecalho': {
            'titulo': 'Relatório de Análise de Riscos',
            'pop': pop_info.get('titulo', 'Processo não identificado'),
            'codigo': pop_info.get('codigo', 'N/A'),
            'macroprocesso': pop_info.get('macroprocesso', 'N/A'),
            'processo': pop_info.get('processo', 'N/A'),
            'subprocesso': pop_info.get('subprocesso', 'N/A'),
            'atividade': pop_info.get('atividade', 'N/A'),
            'responsavel': pop_info.get('responsavel', 'A definir'),
            'data_analise': datetime.now().strftime('%d/%m/%Y')
        },
        'mapa_contexto': {
            'resumo_processo': f"Processo {pop_info.get('titulo', 'não identificado')} envolvendo análise documental, validação normativa e controles administrativos.",
            'partes_interessadas': pop_info.get('operadores', ['Técnico Especializado', 'Apoio-gabinete', 'Coordenador']),
            'sistemas_utilizados': pop_info.get('sistemas', ['Sistema não identificado']),
            'documentos_principais': ['Documentos conforme especificado no POP'],
            'normativos_aplicaveis': pop_info.get('normativos', ['Normativos conforme POP']),
            'pontos_atencao': extract_attention_points(normalized_answers)
        },
        'riscos': risks[:8],
        'matriz_riscos': matriz,
        'analise_categorias': calculate_category_analysis(risks),
        'plano_tratamento': generate_treatment_plan(risks, normalized_answers),
        'sumario_executivo': generate_executive_summary_from_answers(risks, normalized_answers),
        'conclusoes_recomendacoes': generate_fallback_conclusions(risks, normalized_answers)
    }
    return {'success': True, 'data': data}

def _pad_min_risks(risks: List[Dict[str, Any]], pop_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Preenche a lista com riscos genéricos porém úteis, garantindo >=6.
    """
    templates = [
        ('Risco de Comunicação Ineficiente', 'Falta de padrão e SLA de comunicação com órgãos externos gera atrasos', 'Operacional'),
        ('Risco de Integração de Sistemas', 'Integração parcial entre sistemas pode causar inconsistências', 'Tecnológico'),
        ('Risco de Reputação por Atrasos', 'Atrasos recorrentes aumentam reclamações e danos reputacionais', 'Reputacional'),
    ]
    i = 0
    while len(risks) < 6 and i < len(templates):
        title, desc, cat = templates[i]
        risks.append({
            'titulo': title,
            'descricao': desc,
            'categoria': cat,
            'tipo_risco': 'Inerente',
            'probabilidade': 'Média',
            'impacto': 'Médio',
            'severidade': calculate_severity('Média', 'Médio'),
            'apetite_status': 'Não informado',
            'normativo_relacionado': 'Não aplicável',
            'controles_existentes': ['A definir'],
            'tratamento_recomendado': 'Definir plano de ação específico',
            'indicadores_monitoramento': ['A definir'],
            'interdependencias': []
        })
        i += 1
    return risks

def extract_attention_points(normalized_answers: Dict[str, Any]) -> List[str]:
    points = []
    mapping = {
        '12': {'sim': 'Alta taxa de devoluções documentais'},
        '19': {'não': 'Ausência de controles internos'},
        '10': {'não': 'Falta de planos de contingência'},
        '6':  {'não': 'Ausência de plano de backup operacional'},
        '17': {'sim': 'Histórico de reposições ao erário'},
        '18': {'sim': 'Processo trata dados pessoais sensíveis'}
    }
    for q, cond in mapping.items():
        ans = str(normalized_answers.get(q, '')).lower()
        for trig, label in cond.items():
            if ans == trig:
                points.append(label)
    return points or ['Pontos de atenção a serem identificados na análise detalhada']

def infer_contextual_risks_from_answers(pop_info: Dict[str, Any], normalized_answers: Dict[str, Any]) -> List[Dict[str, Any]]:
    risks = []

    # 1: Devoluções >10%
    if normalized_answers.get('12') == 'sim':
        risks.append({
            'titulo': 'Alta Taxa de Devoluções Documentais',
            'descricao': 'Taxa de devoluções superior a 10% gera retrabalho, atraso no atendimento e insatisfação dos usuários',
            'categoria': 'Operacional',
            'tipo_risco': 'Inerente',
            'probabilidade': 'Alta',
            'impacto': 'Médio',
            'severidade': calculate_severity('Alta', 'Médio'),
            'apetite_status': 'Não informado',
            'normativo_relacionado': 'Não aplicável',
            'controles_existentes': ['Validação documental existente'],
            'tratamento_recomendado': 'Implementar checklist de validação prévia e comunicação clara dos requisitos',
            'indicadores_monitoramento': ['% devoluções por tipo de documento', 'Tempo médio de regularização'],
            'interdependencias': []
        })

    # 2: Ausência de controles internos
    if normalized_answers.get('19') == 'não':
        risks.append({
            'titulo': 'Ausência de Controles Internos Formalizados',
            'descricao': 'Processo sem controles formalizados (checklist, dupla validação) e sem monitoramento sistemático de indicadores',
            'categoria': 'Integridade',
            'tipo_risco': 'Inerente',
            'probabilidade': 'Alta',
            'impacto': 'Alto',
            'severidade': calculate_severity('Alta', 'Alto'),
            'apetite_status': 'Não informado',
            'normativo_relacionado': 'Referencial Básico de Governança TCU',
            'controles_existentes': ['Nenhum formalizado'],
            'tratamento_recomendado': 'Implementar framework de controles com dupla validação e logs',
            'indicadores_monitoramento': ['% processos com controles aplicados', 'Taxa de não conformidades'],
            'interdependencias': []
        })

    # 3: Sem plano de contingência de sistemas
    if normalized_answers.get('10') == 'não':
        systems = pop_info.get('sistemas', ['Sistema não identificado'])
        risks.append({
            'titulo': 'Dependência Crítica de Sistemas Sem Contingência',
            'descricao': f'Processo depende de sistemas ({", ".join(systems[:4])}) sem plano de contingência documentado',
            'categoria': 'Tecnológico',
            'tipo_risco': 'Inerente',
            'probabilidade': 'Média',
            'impacto': 'Alto',
            'severidade': calculate_severity('Média', 'Alto'),
            'apetite_status': 'Não informado',
            'normativo_relacionado': 'Não aplicável',
            'controles_existentes': ['Operação padrão nos sistemas'],
            'tratamento_recomendado': 'Criar procedimentos offline e acordos de SLA com TI',
            'indicadores_monitoramento': ['Disponibilidade média', 'MTTR de incidentes'],
            'interdependencias': []
        })

    # 4: Falta de backup de operadores
    if normalized_answers.get('6') == 'não':
        risks.append({
            'titulo': 'Concentração de Conhecimento Crítico',
            'descricao': 'Ausência de plano de substituição para operadores críticos pode causar interrupções operacionais',
            'categoria': 'Operacional',
            'tipo_risco': 'Inerente',
            'probabilidade': 'Média',
            'impacto': 'Alto',
            'severidade': calculate_severity('Média', 'Alto'),
            'apetite_status': 'Não informado',
            'normativo_relacionado': 'Não aplicável',
            'controles_existentes': ['Segregação de funções definida'],
            'tratamento_recomendado': 'Cross-training e documentação de procedimentos críticos',
            'indicadores_monitoramento': ['% operadores com backup', 'Tempo de transferência de conhecimento'],
            'interdependencias': []
        })

    # 5: Reposições ao erário
    if normalized_answers.get('17') == 'sim':
        risks.append({
            'titulo': 'Reincidência de Erros com Reposições ao Erário',
            'descricao': 'Histórico de reposições indica falhas recorrentes em cálculos/validações',
            'categoria': 'Financeiro',
            'tipo_risco': 'Inerente',
            'probabilidade': 'Média',
            'impacto': 'Alto',
            'severidade': calculate_severity('Média', 'Alto'),
            'apetite_status': 'Não informado',
            'normativo_relacionado': 'Art. 230 da Lei 8.112/1990',
            'controles_existentes': ['Procedimentos de acerto em vigor'],
            'tratamento_recomendado': 'Dupla conferência e automatização de cálculos',
            'indicadores_monitoramento': ['Valor mensal de reposições', 'Taxa de erros em cálculos'],
            'interdependencias': []
        })

    # 6: LGPD sensível
    if normalized_answers.get('18') == 'sim':
        risks.append({
            'titulo': 'Conformidade LGPD no Tratamento de Dados',
            'descricao': 'Tratamento de dados pessoais sensíveis requer controles de privacidade e proteção',
            'categoria': 'Normativo',
            'tipo_risco': 'Residual',
            'probabilidade': 'Média',
            'impacto': 'Alto',
            'severidade': calculate_severity('Média', 'Alto'),
            'apetite_status': 'Não informado',
            'normativo_relacionado': 'Lei 13.709/2018 (LGPD)',
            'controles_existentes': ['Tratamento conforme finalidade institucional'],
            'tratamento_recomendado': 'Formalizar base legal, minimização e registro de atividades',
            'indicadores_monitoramento': ['% conformidade LGPD', 'Incidentes de vazamento'],
            'interdependencias': []
        })

    # 7: Conflito normativo
    if normalized_answers.get('3') in ['alto', 'médio']:
        lvl = 'Alta' if normalized_answers.get('3') == 'alto' else 'Média'
        sev = calculate_severity(lvl, 'Alto' if lvl == 'Alta' else 'Médio')
        risks.append({
            'titulo': 'Risco de Desatualização/Conflito Normativo',
            'descricao': 'Possível conflito ou defasagem entre normativos aplicáveis ao processo',
            'categoria': 'Normativo',
            'tipo_risco': 'Residual',
            'probabilidade': 'Alta' if lvl == 'Alta' else 'Média',
            'impacto': 'Alto' if lvl == 'Alta' else 'Médio',
            'severidade': sev,
            'apetite_status': 'Não informado',
            'normativo_relacionado': 'Normativos listados no POP',
            'controles_existentes': ['Acompanhamento normativo parcial'],
            'tratamento_recomendado': 'Rotina de revisão normativa e treinamento da equipe',
            'indicadores_monitoramento': ['Tempo para atualização', 'Nº de não conformidades por norma'],
            'interdependencias': []
        })

    return risks[:10]

def calculate_risk_matrix_from_risks(risks: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {'criticos': 0, 'altos': 0, 'moderados': 0, 'baixos': 0}
    for r in risks:
        sev = str(r.get('severidade', '')).lower()
        if sev == 'crítico':
            counts['criticos'] += 1
        elif sev == 'alto':
            counts['altos'] += 1
        elif sev == 'moderado':
            counts['moderados'] += 1
        else:
            counts['baixos'] += 1
    return counts

def generate_treatment_plan(risks: List[Dict[str, Any]], normalized_answers: Dict[str, Any]) -> Dict[str, Any]:
    high = [r for r in risks if r.get('severidade') in ['Crítico', 'Alto']]
    immediate = []
    for r in high[:4]:
        t = r.get('tratamento_recomendado', '')
        if t and 'Definir tratamento específico' not in t:
            immediate.append(t)
    if normalized_answers.get('19') == 'não':
        immediate.append('Implementar controles internos básicos')
    if normalized_answers.get('10') == 'não':
        immediate.append('Desenvolver planos de contingência para sistemas críticos')

    return {
        'mitigacao_imediata': immediate[:5] or ['Análise detalhada dos riscos identificados'],
        'monitoramento': ['Implementar indicadores de performance', 'Revisar eficácia dos controles trimestralmente'],
        'lacunas_controle': ['Formalização de controles internos', 'Documentação de procedimentos críticos'],
        'sugestoes_indicadores': ['Taxa de conformidade', 'Lead time por etapa', 'Retrabalho por motivo', 'Disponibilidade dos sistemas'],
        'interdependencias_criticas': ['Dependência entre sistemas e procedimentos manuais', 'Relação entre qualificação da equipe e qualidade dos resultados']
    }

def generate_executive_summary_from_answers(risks: List[Dict[str, Any]], normalized_answers: Dict[str, Any]) -> Dict[str, Any]:
    high = [r['titulo'] for r in risks if r.get('severidade') in ['Crítico', 'Alto']]
    insights = []
    if normalized_answers.get('12') == 'sim':
        insights.append("taxa de devoluções >10%")
    if normalized_answers.get('17') == 'sim':
        insights.append("histórico de reposições")
    if normalized_answers.get('19') == 'não':
        insights.append("ausência de controles")
    return {
        'maiores_riscos': high[:5],
        'areas_criticas': ['Controles internos', 'Dependência tecnológica', 'Gestão documental'],
        'acoes_urgentes': ['Implementar controles internos', 'Desenvolver planos de contingência', 'Estabelecer indicadores de monitoramento'],
        'sintese_gerencial': f'Análise identifica {len(risks)} riscos, {len(high)} críticos/altos. Vulnerabilidades em {", ".join(insights) if insights else "múltiplas dimensões"}. Priorizar controles, treinamento e indicadores.'
    }

def generate_fallback_conclusions(risks: List[Dict[str, Any]], normalized_answers: Dict[str, Any]) -> str:
    crit = len([r for r in risks if r.get('severidade') == 'Crítico'])
    high = len([r for r in risks if r.get('severidade') == 'Alto'])
    control_status = "crítica" if normalized_answers.get('19') == 'não' else "adequada"
    return f"Análise em modo de recuperação identificou {len(risks)} riscos ({crit} críticos, {high} altos). Situação de controles internos {control_status}. Priorizar implementação de controles, indicadores e contingência; executar nova análise completa para validação final."

# =========================
# Logs para auditoria
# =========================

def save_analysis_log(helena_response: Optional[str], final_report: Optional[Dict[str, Any]], success: bool=True) -> None:
    preview = (helena_response or "")[:400]
    counts = len(final_report.get('riscos', [])) if final_report else 0
    cats = list(final_report.get('analise_categorias', {}).keys()) if final_report else []
    entry = {
        'timestamp': datetime.now().isoformat(),
        'success': success,
        'helena_response_length': len(helena_response or ""),
        'helena_response_preview': preview,
        'final_report_risks_count': counts,
        'final_report_categories': cats
    }
    logger.info(f"[save_analysis_log] {json.dumps(entry, ensure_ascii=False)}")

    try:
        # Salva arquivo leve para auditoria (opcional; comentar se não desejar I/O)
        digest = hashlib.sha256((preview + str(counts)).encode()).hexdigest()[:10]
        fname = f'analysis_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{digest}.json'
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)
        logger.info(f"[save_analysis_log] Log salvo em {fname}")
    except Exception as e:
        logger.warning(f"[save_analysis_log] Falha ao salvar log em arquivo: {e}")
        
