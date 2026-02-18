"""
Validacao final do PDF POP — checklist de pronto.

Testa:
  1. POP vazio exporta PDF
  2. POP linear (docs + detalhes + tempo)
  3. POP condicional (antes_decisao + cenarios + subetapas)
  4. Tabela de documentos com dados completos e incompletos
  5. Caracteres especiais (acentos, travessao)
  6. KeepTogether com bloco condicional grande (sem pagina em branco)
  7. Fallbacks: dict incompleto, lista vazia, string legado
"""
import os
import sys
import traceback

# Ajusta path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from processos.export.pop_adapter import preparar_pop_para_pdf
from processos.utils import PDFGenerator

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'media', 'pdfs', 'test_validation')
os.makedirs(OUTPUT_DIR, exist_ok=True)

gen = PDFGenerator()
results = []


def test(nome, dados_pop):
    """Testa geracao de PDF e reporta resultado."""
    try:
        dados = preparar_pop_para_pdf(dados_pop)
        arquivo = f"test_{nome}.pdf"
        caminho = gen.gerar_pop_completo(dados, arquivo)
        if caminho and os.path.exists(caminho):
            tamanho = os.path.getsize(caminho)
            results.append((nome, "OK", f"{tamanho:,} bytes"))
            # Move para pasta de teste
            dest = os.path.join(OUTPUT_DIR, arquivo)
            if os.path.exists(dest):
                os.remove(dest)
            os.rename(caminho, dest)
        else:
            results.append((nome, "FALHOU", "gerar_pop_completo retornou None"))
    except Exception as e:
        results.append((nome, "ERRO", f"{type(e).__name__}: {e}"))
        traceback.print_exc()


# =============================================================================
# 1. POP VAZIO
# =============================================================================
test("01_vazio", {
    "nome_processo": "Processo Vazio (teste)",
})

# =============================================================================
# 2. POP LINEAR (docs + detalhes + tempo)
# =============================================================================
test("02_linear", {
    "nome_processo": "Concessao de Licenca Capacitacao",
    "area": "CGBEN",
    "codigo_cap": "02.03.03.01.001",
    "macroprocesso": "Gestao de Pessoas",
    "processo_especifico": "Capacitacao",
    "subprocesso": "Licenca Capacitacao",
    "entrega_esperada": "Portaria de concessao publicada no DOU",
    "dispositivos_normativos": "Decreto 9991/2019, IN 21/2021",
    "sistemas": ["SEI", "SIAPE", "SIGEPE"],
    "operadores": ["Analista de RH", "Coordenador CGBEN"],
    "etapas": [
        {
            "numero": "1",
            "descricao": "Receber requerimento via SEI",
            "operador_nome": "Analista de RH",
            "sistemas": ["SEI"],
            "docs_requeridos": ["Requerimento", "Plano de Atividades"],
            "docs_gerados": ["Despacho de Recebimento"],
            "detalhes": ["Verificar numeracao do processo", "Conferir dados do servidor"],
            "tempo_estimado": "30 minutos",
        },
        {
            "numero": "2",
            "descricao": "Analisar conformidade documental",
            "operador_nome": "Analista de RH",
            "sistemas": ["SEI", "SIAPE"],
            "docs_requeridos": ["Requerimento", "CPF"],
            "docs_gerados": ["Nota Tecnica"],
            "detalhes": ["Consultar situacao funcional no SIAPE", "Verificar tempo de servico"],
            "tempo_estimado": "2 horas",
        },
    ],
    "documentos_utilizados": [
        {"tipo_documento": "Requerimento", "descricao": "Pedido formal do servidor", "tipo_uso": "Utilizado", "obrigatorio": True, "sistema": "SEI"},
        {"tipo_documento": "Nota Tecnica", "descricao": "Parecer da area", "tipo_uso": "Gerado", "obrigatorio": True, "sistema": "SEI"},
        {"tipo_documento": "Plano de Atividades", "descricao": "", "tipo_uso": "Utilizado", "obrigatorio": False, "sistema": ""},
    ],
    "pontos_atencao": "Verificar se servidor tem 5 anos de efetivo exercicio",
    "fluxos_entrada": ["Requerimento do servidor", "Despacho da chefia"],
    "fluxos_saida": ["Portaria publicada", "Notificacao ao servidor"],
})

# =============================================================================
# 3. POP CONDICIONAL (antes_decisao + cenarios + subetapas)
# =============================================================================
test("03_condicional", {
    "nome_processo": "Ressarcimento de Plano de Saude",
    "area": "CGBEN",
    "codigo_cap": "02.01.01.01.003",
    "macroprocesso": "Gestao de Pessoas",
    "processo_especifico": "Beneficios",
    "subprocesso": "Assistencia a Saude",
    "entrega_esperada": "Ressarcimento processado na folha de pagamento",
    "dispositivos_normativos": "IN 97/2022 Art. 34-42, Decreto 4978/2004",
    "sistemas": ["SEI", "SIAPE", "SIGEPE"],
    "operadores": ["Analista CGBEN", "Gestor CGBEN"],
    "etapas": [
        {
            "numero": "1",
            "descricao": "Receber requerimento de ressarcimento",
            "operador_nome": "Analista CGBEN",
            "sistemas": ["SEI"],
            "docs_requeridos": ["Requerimento", "Comprovante de pagamento"],
            "docs_gerados": [],
            "detalhes": ["Conferir dados pessoais", "Verificar prazo"],
            "tempo_estimado": "20 minutos",
        },
        {
            "numero": "2",
            "descricao": "Analisar elegibilidade do servidor",
            "operador_nome": "Analista CGBEN",
            "sistemas": ["SIAPE", "SIGEPE"],
            "docs_requeridos": [],
            "docs_gerados": ["Parecer tecnico"],
            "tipo": "condicional",
            "tipo_condicional": "binario",
            "pergunta_decisao": "Servidor elegivel para ressarcimento?",
            "antes_decisao": {
                "numero": "2.1",
                "descricao": "Consultar situacao funcional no SIAPE e verificar vinculo ativo"
            },
            "cenarios": [
                {
                    "numero": "2.2",
                    "descricao": "Servidor elegivel",
                    "subetapas": [
                        {"numero": "2.2.1", "descricao": "Elaborar parecer favoravel"},
                        {"numero": "2.2.2", "descricao": "Calcular valor do ressarcimento"},
                        {"numero": "2.2.3", "descricao": "Encaminhar para aprovacao da chefia"},
                    ]
                },
                {
                    "numero": "2.3",
                    "descricao": "Servidor inelegivel",
                    "subetapas": [
                        {"numero": "2.3.1", "descricao": "Elaborar parecer desfavoravel"},
                        {"numero": "2.3.2", "descricao": "Notificar servidor com fundamentacao legal"},
                    ]
                }
            ],
            "tempo_estimado": "1 hora",
        },
        {
            "numero": "3",
            "descricao": "Processar pagamento na folha",
            "operador_nome": "Gestor CGBEN",
            "sistemas": ["SIAPE"],
            "docs_requeridos": ["Parecer tecnico aprovado"],
            "docs_gerados": ["Ordem de pagamento"],
            "detalhes": ["Lancar valores no SIAPE", "Verificar folha vigente"],
            "tempo_estimado": "45 minutos",
        },
    ],
    "documentos_utilizados": [
        {"tipo_documento": "Requerimento", "descricao": "Pedido de ressarcimento", "tipo_uso": "Utilizado", "obrigatorio": True, "sistema": "SEI"},
        {"tipo_documento": "Comprovante", "descricao": "Comprovante de pagamento do plano", "tipo_uso": "Utilizado", "obrigatorio": True, "sistema": ""},
        {"tipo_documento": "Parecer Tecnico", "descricao": "Analise de elegibilidade", "tipo_uso": "Gerado", "obrigatorio": True, "sistema": "SEI"},
    ],
    "pontos_atencao": "Prazo maximo de 30 dias para ressarcimento apos requerimento",
})

# =============================================================================
# 4. CARACTERES ESPECIAIS (acentos, travessao, cedilha)
# =============================================================================
test("04_caracteres_especiais", {
    "nome_processo": "Concessão de Licença — Análise Prévia",
    "area": "CGBEN — Coordenação-Geral",
    "entrega_esperada": "Portaria de concessão publicada — após análise técnica",
    "dispositivos_normativos": "Instrução Normativa nº 97/2022 — Art. 34 a 42",
    "etapas": [
        {
            "numero": "1",
            "descricao": "Receber requerimento — verificar documentação prévia",
            "operador_nome": "Técnico Administrativo — Seção de RH",
            "sistemas": ["SEI — Sistema Eletrônico de Informações"],
            "docs_requeridos": ["Requerimento padrão (Formulário nº 3)"],
            "docs_gerados": ["Despacho de recebimento — via SEI"],
            "detalhes": [
                "Conferir cédula de identidade",
                "Verificar situação funcional — SIAPE",
                "Emitir comprovante de recebimento (padrão DECIPEX)",
            ],
        },
    ],
    "documentos_utilizados": [
        {"tipo_documento": "Instrução Normativa", "descricao": "IN nº 97 — disposições gerais", "tipo_uso": "Utilizado", "obrigatorio": True, "sistema": "SEI"},
    ],
})

# =============================================================================
# 5. KEEPTOGETHER — BLOCO CONDICIONAL GRANDE (muitos cenarios/subetapas)
# =============================================================================
test("05_keeptogether_grande", {
    "nome_processo": "Processo com Condicional Extensa",
    "area": "Teste",
    "etapas": [
        {
            "numero": "1",
            "descricao": "Etapa com decisao complexa e muitas ramificacoes",
            "operador_nome": "Analista Senior",
            "tipo": "condicional",
            "tipo_condicional": "multiplos",
            "pergunta_decisao": "Qual o resultado da analise detalhada?",
            "antes_decisao": {
                "numero": "1.1",
                "descricao": (
                    "Realizar analise completa da documentacao apresentada, "
                    "incluindo verificacao de autenticidade, conferencia de dados, "
                    "validacao cruzada com sistemas externos, consulta a base de "
                    "dados historica e elaboracao de relatorio preliminar com todas "
                    "as evidencias coletadas durante o processo de analise."
                )
            },
            "cenarios": [
                {
                    "numero": "1.2",
                    "descricao": "Cenario A — Documentacao completa e regular",
                    "subetapas": [
                        {"numero": "1.2.1", "descricao": "Elaborar parecer favoravel com fundamentacao"},
                        {"numero": "1.2.2", "descricao": "Encaminhar para aprovacao da chefia imediata"},
                        {"numero": "1.2.3", "descricao": "Aguardar retorno e registrar no SEI"},
                        {"numero": "1.2.4", "descricao": "Publicar decisao no DOU"},
                        {"numero": "1.2.5", "descricao": "Notificar interessado por email institucional"},
                    ]
                },
                {
                    "numero": "1.3",
                    "descricao": "Cenario B — Documentacao incompleta",
                    "subetapas": [
                        {"numero": "1.3.1", "descricao": "Identificar documentos faltantes"},
                        {"numero": "1.3.2", "descricao": "Elaborar notificacao de pendencia"},
                        {"numero": "1.3.3", "descricao": "Enviar notificacao via SEI"},
                        {"numero": "1.3.4", "descricao": "Aguardar complementacao (prazo 30 dias)"},
                    ]
                },
                {
                    "numero": "1.4",
                    "descricao": "Cenario C — Documentacao com irregularidade",
                    "subetapas": [
                        {"numero": "1.4.1", "descricao": "Registrar irregularidade encontrada"},
                        {"numero": "1.4.2", "descricao": "Elaborar parecer desfavoravel fundamentado"},
                        {"numero": "1.4.3", "descricao": "Encaminhar para analise juridica (CONJUR)"},
                        {"numero": "1.4.4", "descricao": "Aguardar parecer juridico"},
                        {"numero": "1.4.5", "descricao": "Notificar interessado com direito a recurso"},
                        {"numero": "1.4.6", "descricao": "Registrar decisao final no sistema"},
                    ]
                },
            ],
        },
        # Etapa 2 simples para garantir que aparece apos o bloco grande
        {
            "numero": "2",
            "descricao": "Arquivar processo",
            "operador_nome": "Assistente Administrativo",
            "detalhes": ["Conferir documentacao final", "Arquivar no SEI"],
        },
    ],
})

# =============================================================================
# 6. FALLBACKS — dict incompleto, campos None, lista vazia
# =============================================================================
test("06_fallbacks", {
    "nome_processo": "Teste de Fallbacks",
    "area": None,  # None em campo string
    "etapas": [
        # Etapa com dict quase vazio
        {"descricao": "So descricao, sem nada mais"},
        # Etapa com campos None
        {
            "numero": "2",
            "descricao": "Campos None",
            "operador_nome": None,
            "sistemas": None,
            "docs_requeridos": None,
            "docs_gerados": "uma string ao inves de lista",
            "detalhes": None,
        },
        # Etapa condicional com cenario sem subetapas
        {
            "numero": "3",
            "descricao": "Condicional incompleta",
            "tipo": "condicional",
            "antes_decisao": "string ao inves de dict",
            "cenarios": [
                {"descricao": "Cenario sem numero nem subetapas"},
                {},  # Cenario completamente vazio
            ],
        },
    ],
    # Documentos: mix de formatos
    "documentos_utilizados": [
        {"tipo_documento": "Doc Completo", "descricao": "Com todos os campos", "tipo_uso": "Utilizado", "obrigatorio": True, "sistema": "SEI"},
        {"tipo_documento": "Doc Minimo"},  # Sem descricao, uso, obrigatorio, sistema
        {},  # Dict vazio
        "uma string solta",  # Nao e dict
    ],
})

# =============================================================================
# 7. DOCUMENTOS LEGADO (string pura)
# =============================================================================
test("07_docs_string_legado", {
    "nome_processo": "POP Legado com Documentos String",
    "area": "CGBEN",
    "etapas": [
        {"numero": "1", "descricao": "Etapa unica"},
    ],
    "documentos_utilizados": "Requerimento, CPF, Comprovante de Residencia, Certidao de Nascimento",
})

# =============================================================================
# RESULTADO FINAL
# =============================================================================
print("\n" + "=" * 70)
print("CHECKLIST DE VALIDACAO — PDF POP")
print("=" * 70)
ok_count = 0
for nome, status, detalhe in results:
    icon = "PASS" if status == "OK" else "FAIL"
    print(f"  [{icon}] {nome}: {detalhe}")
    if status == "OK":
        ok_count += 1

print(f"\n  Resultado: {ok_count}/{len(results)} testes passaram")
print(f"  PDFs gerados em: {os.path.abspath(OUTPUT_DIR)}")
print("=" * 70)

if ok_count < len(results):
    sys.exit(1)
