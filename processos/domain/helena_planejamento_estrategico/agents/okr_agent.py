import copy
from typing import Dict, Any
from langchain_openai import ChatOpenAI
import re
from processos.domain.helena_semantic_planner import HelenaSemanticPlanner

class OKRNaturalAgent:
    """
    Helena OKR Natural – parceira estratégica, não formulário.
    Não há etapas, apenas campos que o usuário preenche naturalmente.
    Helena apenas guia e traduz a fala em conceitos de OKR.

    Usa HelenaSemanticPlanner para interpretação semântica robusta.
    """

    def __init__(self, llm: ChatOpenAI | None = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7, request_timeout=30)
        self.planner = HelenaSemanticPlanner()

    # =========================================================================
    # SHIM DE COMPATIBILIDADE COM ORQUESTRADOR
    # =========================================================================

    def processar_mensagem(self, mensagem: str, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        """
        Método de compatibilidade com o orquestrador.

        Mantém a assinatura esperada pelo pe_orchestrator.py:
        - Recebe estrutura_atual (dict)
        - Retorna {'campo', 'valor', 'proxima_pergunta', 'completo', 'percentual', 'validacao_ok'}
        """
        contexto = self._init_contexto(estrutura_atual)
        bruto = self.processar(mensagem, contexto)  # Chama método interno
        return self._to_orchestrator(bruto, contexto)

    # =========================================================================
    # LÓGICA INTERNA (FORMATO SEMÂNTICO)
    # =========================================================================

    def processar(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do usuário usando interpretação semântica.

        Returns formato interno:
            {
                'acao': str,      # criar_objetivo, pedir_krs, etc.
                'texto': str,     # Mensagem para o usuário
                'payload': dict   # Dados adicionais
            }
        """
        msg = mensagem.lower().strip()

        # Inicializa estrutura
        if "modelo" not in contexto:
            contexto["modelo"] = "okr"
        contexto.setdefault("objetivos", [])

        # 👋 Boas-vindas
        if any(p in msg for p in ["oi", "olá", "bom dia", "começar", "iniciar", "start"]):
            return {
                "acao": "boas_vindas",
                "texto": (
                    "Oi 👋 Que bom te ver por aqui. Vamos trabalhar com **OKRs**.\n\n"
                    "Esse método ajuda a transformar ideias em metas com significado.\n"
                    "Nada de formulário, só conversa natural.\n\n"
                    "Três pilares pra lembrar:\n"
                    "🎯 Objetivo — o que você quer alcançar\n"
                    "📊 Resultados-Chave — como saber se chegou lá\n"
                    "📅 Período — quando pretende atingir\n\n"
                    "Quer começar me contando o que está te motivando a fazer OKRs agora?"
                ),
                "payload": {}
            }

        # ❓ Pedidos de ajuda
        if any(p in msg for p in ["não sei", "ajuda", "explica", "entender", "como funciona"]):
            return {
                "acao": "explicar_okr",
                "texto": (
                    "Claro 😊 O método OKR é simples: ajuda a alinhar pessoas e medir progresso.\n\n"
                    "🎯 **Objetivo**: o que você quer mudar ou melhorar\n"
                    "📊 **Key Results**: as evidências numéricas de que você está avançando\n"
                    "📅 **Período**: horizonte de tempo pra revisar e ajustar\n\n"
                    "Quer que eu te ajude a transformar algo da sua rotina em um OKR?"
                ),
                "payload": {}
            }

        # 🔁 REFINAMENTO DE OBJETIVO EXISTENTE (verifica antes da interpretação semântica)
        if any(p in msg for p in ["não parece", "mais profissional", "melhorar esse objetivo", "ajustar objetivo", "refazer", "não está bom", "não gostei", "reescrever"]):
            ultimo_obj = contexto["objetivos"][-1]["titulo"] if contexto.get("objetivos") else None

            if not ultimo_obj:
                return {
                    "acao": "ajuda_contextual",
                    "texto": "Não tenho um objetivo anterior para refinar. Me conta o que você quer alcançar?",
                    "payload": {}
                }

            return {
                "acao": "refinar_objetivo",
                "texto": (
                    f"Entendi 😉 Quer deixar o objetivo mais claro ou mais estratégico?\n"
                    f"Posso reformular **\"{ultimo_obj}\"** com outro tom — por exemplo:\n\n"
                    f"- 'Fortalecer a gestão da equipe e melhorar a organização das entregas'\n"
                    f"ou\n"
                    f"- 'Aprimorar a coordenação das tarefas da equipe com foco em resultados'\n\n"
                    "Qual dessas versões soa mais adequada, ou quer que eu crie uma nova formulação?"
                ),
                "payload": {"ultimo_objetivo": ultimo_obj}
            }

        # 🧠 INTERPRETAÇÃO SEMÂNTICA PRINCIPAL
        interpretacao = self.planner.interpretar(mensagem)
        tipo = interpretacao.get('tipo')

        # CAMPO: PROBLEMA → Converte em Objetivo
        if tipo == 'problema':
            objetivo = self.planner._inverter_problema_generico(mensagem)

            # Adiciona objetivo temporário ao contexto para permitir refinamento
            contexto["objetivos"].append({
                "titulo": objetivo,
                "resultados_chave": [],
                "iniciativas": [],
                "confirmado": False  # Marca como pendente
            })

            return {
                "acao": "criar_objetivo",
                "texto": (
                    f"💡 Entendi o que você quis dizer.\n"
                    f"Podemos transformar isso em um objetivo estratégico:\n"
                    f"**{objetivo}**\n\n"
                    "Faz sentido pra você?"
                ),
                "payload": {"objetivo": objetivo}
            }

        # CAMPO: OBJETIVO (já formulado)
        if tipo == 'objetivo':
            # Se usuário digitou apenas "objetivo" isolado, pergunta o que ele quer
            if msg in ['objetivo', 'objetivos']:
                return {
                    "acao": "pedir_objetivo",
                    "texto": "Legal 🎯 Me conta — o que você quer alcançar ou mudar na sua área?",
                    "payload": {}
                }

            obj_refinado = self.planner._refinar_objetivo_generico(mensagem)
            contexto["objetivos"].append({
                "titulo": obj_refinado,
                "resultados_chave": [],
                "iniciativas": []
            })

            return {
                "acao": "pedir_krs",
                "texto": (
                    f"🎯 Perfeito. Seu objetivo pode ser formulado assim:\n"
                    f"**{obj_refinado}**\n\n"
                    "Agora vamos pensar nos resultados-chave.\n"
                    "Como você vai saber que está progredindo?"
                ),
                "payload": {"indice_objetivo": len(contexto["objetivos"]) - 1}
            }

        # CAMPO: RESULTADO (KR mensurável)
        if tipo == 'resultado':
            # Se usuário digitou apenas "resultado", "kr", pergunta quais são
            if msg in ['resultado', 'resultados', 'kr', 'krs', 'resultado-chave', 'resultados-chave']:
                return {
                    "acao": "pedir_krs",
                    "texto": "Ótimo 📊 Quais seriam os resultados que mostrariam progresso?",
                    "payload": {}
                }

            # Tenta anexar KRs ao último objetivo
            if not contexto["objetivos"]:
                return {
                    "acao": "erro_sem_objetivo",
                    "texto": "Antes de definir resultados, precisamos de um objetivo. O que você quer alcançar?",
                    "payload": {}
                }

            idx = len(contexto["objetivos"]) - 1
            krs = self.planner.extrair_lista(mensagem) or [mensagem.strip()]
            krs_validos = [kr for kr in krs if self.planner.validar_mensurabilidade(kr)]

            if not krs_validos:
                return {
                    "acao": "reforcar_mensurabilidade",
                    "texto": (
                        "Entendi. Mas pra ser um KR, precisa ser mensurável.\n"
                        "Tenta incluir um número, percentual ou prazo.\n"
                        "Exemplo: 'Aumentar de 60% para 85%'"
                    ),
                    "payload": {}
                }

            contexto["objetivos"][idx]["resultados_chave"].extend(krs_validos)
            total_krs = len(contexto["objetivos"][idx]["resultados_chave"])

            return {
                "acao": "pos_krs",
                "texto": (
                    f"📊 Resultado registrado!\n"
                    f"Até agora temos {total_krs} KR{'s' if total_krs > 1 else ''}.\n\n"
                    "Quer adicionar mais ou revisar o que já temos?"
                ),
                "payload": {}
            }

        # CONFIRMAÇÕES (sim, confirma, ok, etc.)
        if msg in ['sim', 'confirma', 'confirmo', 'ok', 'certo', 'isso', 'exato']:
            return self._processar_confirmacao(contexto)

        # NEGAÇÕES (não, negativo, etc.)
        if msg in ['não', 'nao', 'negativo', 'errado']:
            return {
                "acao": "ajuste",
                "texto": "Sem problemas. Me conta como você gostaria de ajustar.",
                "payload": {}
            }

        # DETECÇÃO DE PERÍODO
        if self._detectar_periodo(mensagem):
            periodo = self._extrair_periodo(mensagem)
            contexto["periodo"] = periodo

            # Se já tem objetivo e KRs, pode finalizar
            if contexto.get("objetivos") and any(obj.get("resultados_chave") for obj in contexto["objetivos"]):
                return {
                    "acao": "finalizar",
                    "texto": f"Perfeito! 📅 Período definido: **{periodo}**.\n\nVamos revisar seu OKR completo?",
                    "payload": {"periodo": periodo}
                }
            else:
                return {
                    "acao": "periodo_definido",
                    "texto": f"📅 Período definido: **{periodo}**",
                    "payload": {"periodo": periodo}
                }

        # CASO NEUTRO: Ajuda contextual
        return {
            "acao": "ajuda_contextual",
            "texto": "Entendi. Me conta com suas palavras o que está te incomodando ou o que você quer melhorar. Eu te ajudo a transformar isso em um OKR.",
            "payload": {}
        }

    # =========================================================================
    # MÉTODOS AUXILIARES
    # =========================================================================

    def _processar_confirmacao(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Processa confirmação do usuário e avança no fluxo natural."""

        # Se tem objetivo pendente mas não confirmado, confirma
        if contexto.get("objetivos") and not contexto["objetivos"][-1].get("resultados_chave"):
            return {
                "acao": "pedir_krs",
                "texto": (
                    "Perfeito! 🎯\n\n"
                    "Agora vamos pensar nos resultados-chave.\n"
                    "Como você vai saber que está progredindo nesse objetivo?"
                ),
                "payload": {}
            }

        # Se tem objetivo e KRs, pergunta sobre período
        if contexto.get("objetivos") and any(obj.get("resultados_chave") for obj in contexto["objetivos"]) and not contexto.get("periodo"):
            return {
                "acao": "pedir_periodo",
                "texto": (
                    "Legal! 📊\n\n"
                    "Esses resultados são para os próximos 3 meses, 6 meses ou o ano todo?"
                ),
                "payload": {}
            }

        # Se tem tudo, gera resumo
        if contexto.get("objetivos") and any(obj.get("resultados_chave") for obj in contexto["objetivos"]) and contexto.get("periodo"):
            return self._gerar_resumo_okr(contexto)

        # Confirmação genérica
        return {
            "acao": "confirmacao_generica",
            "texto": "Beleza! Pode continuar.",
            "payload": {}
        }

    def _gerar_resumo_okr(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo estruturado do OKR criado."""
        objetivos = contexto.get("objetivos", [])
        periodo = contexto.get("periodo", "Não definido")

        if not objetivos:
            return {
                "acao": "erro_resumo",
                "texto": "Não há objetivos definidos ainda.",
                "payload": {}
            }

        # Monta resumo
        linhas = ["✅ Pronto! Aqui está seu OKR:\n"]

        for i, obj in enumerate(objetivos, 1):
            linhas.append(f"**🎯 Objetivo {i}:**")
            linhas.append(f"{obj['titulo']}\n")

            if obj.get('resultados_chave'):
                linhas.append(f"**📊 Resultados-Chave:**")
                for kr in obj['resultados_chave']:
                    linhas.append(f"  - {kr}")
                linhas.append("")

        linhas.append(f"**📅 Período:** {periodo}\n")
        linhas.append("Quer salvar ou ajustar algo?")

        return {
            "acao": "resumo_final",
            "texto": "\n".join(linhas),
            "payload": {
                "okr_completo": {
                    "objetivos": objetivos,
                    "periodo": periodo
                }
            }
        }

    def _detectar_periodo(self, mensagem: str) -> bool:
        """Detecta se mensagem contém indicação de período temporal."""
        msg = mensagem.lower()
        padroes_periodo = [
            r'\d+\s*meses?',
            r'\d+\s*anos?',
            r'\d+\s*trimestres?',
            r'\d+\s*semestres?',
            r'\d+\s*semanas?',
            'trimestre', 'semestre', 'anual', 'mensal', 'semanal'
        ]

        for padrao in padroes_periodo:
            if re.search(padrao, msg):
                return True
        return False

    def _extrair_periodo(self, mensagem: str) -> str:
        """Extrai descrição do período da mensagem."""
        msg = mensagem.lower().strip()

        # Padrões numéricos (3 meses, 6 meses, 1 ano, etc.)
        match = re.search(r'(\d+)\s*(mes(?:es)?|ano(?:s)?|trimestre(?:s)?|semestre(?:s)?|semana(?:s)?)', msg)
        if match:
            numero = match.group(1)
            unidade = match.group(2)

            # Normaliza plural
            if 'mes' in unidade:
                unidade_norm = 'mês' if numero == '1' else 'meses'
            elif 'ano' in unidade:
                unidade_norm = 'ano' if numero == '1' else 'anos'
            elif 'trimestre' in unidade:
                unidade_norm = 'trimestre' if numero == '1' else 'trimestres'
            elif 'semestre' in unidade:
                unidade_norm = 'semestre' if numero == '1' else 'semestres'
            elif 'semana' in unidade:
                unidade_norm = 'semana' if numero == '1' else 'semanas'
            else:
                unidade_norm = unidade

            return f"{numero} {unidade_norm}"

        # Padrões textuais
        if 'trimestre' in msg:
            return "1 trimestre (3 meses)"
        elif 'semestre' in msg:
            return "1 semestre (6 meses)"
        elif 'anual' in msg or 'ano' in msg:
            return "1 ano"
        elif 'mensal' in msg:
            return "1 mês"

        # Fallback: retorna a mensagem original capitalizada
        return mensagem.strip().capitalize()

    # =========================================================================
    # CONVERSORES DE FORMATO
    # =========================================================================

    def _init_contexto(self, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        """Inicializa contexto a partir da estrutura do orquestrador."""
        ctx = copy.deepcopy(estrutura_atual or {})
        ctx.setdefault("modelo", "okr")
        ctx.setdefault("objetivos", [])
        ctx.setdefault("periodo", None)
        return ctx

    def _to_orchestrator(self, bruto: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte formato interno {acao, texto, payload} para contrato do orquestrador:
        {'campo', 'valor', 'proxima_pergunta', 'completo', 'percentual', 'validacao_ok'}
        """
        acao = bruto.get("acao")
        texto = bruto.get("texto", "")
        payload = bruto.get("payload", {})

        # Mapeamento de ações → campo/valor
        mapeamento = {
            "boas_vindas": ("inicio", None, True),
            "explicar_okr": ("ajuda", None, True),
            "pedir_objetivo": ("solicitar_objetivo", None, True),
            "criar_objetivo": ("objetivo_proposto", payload.get("objetivo"), True),
            "refinar_objetivo": ("refinar_objetivo", payload.get("ultimo_objetivo"), True),
            "pedir_krs": ("solicitar_krs", None, True),
            "erro_sem_objetivo": ("erro_validacao", None, False),
            "reforcar_mensurabilidade": ("erro_validacao", None, False),
            "pos_krs": ("resultados_chave", None, True),
            "ajuste": ("ajuste", None, True),
            "pedir_periodo": ("solicitar_periodo", None, True),
            "periodo_definido": ("periodo", payload.get("periodo"), True),
            "finalizar": ("pronto_para_revisao", None, True),
            "resumo_final": ("resumo", payload.get("okr_completo"), True),
            "confirmacao_generica": ("confirmacao", None, True),
            "ajuda_contextual": ("ajuda", None, True),
        }

        campo, valor, validacao_ok = mapeamento.get(acao, ("neutro", None, True))

        return {
            "campo": campo,
            "valor": valor,
            "proxima_pergunta": texto,
            "completo": acao == "resumo_final",
            "percentual": self._calc_percentual(contexto),
            "validacao_ok": validacao_ok
        }

    def _calc_percentual(self, contexto: Dict[str, Any]) -> int:
        """Calcula percentual de conclusão do OKR."""
        if not contexto.get("objetivos"):
            return 10

        base = 30 + min(len(contexto["objetivos"]) * 10, 30)

        # Bonus se último objetivo já tem KRs
        if contexto["objetivos"] and contexto["objetivos"][-1].get("resultados_chave"):
            base += 20

        # Bonus se tem período
        if contexto.get("periodo"):
            base += 20

        return min(base, 95)


# Alias para manter compatibilidade
OKRAgent = OKRNaturalAgent
