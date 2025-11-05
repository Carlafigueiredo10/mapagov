import copy
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
import re
from processos.domain.helena_semantic_planner import HelenaSemanticPlanner

class FlowchartAgent:
    """
    Helena Flowchart Agent – parceira conversacional para mapeamento de processos.
    Extrai etapas, decisões, responsáveis e sistemas de forma natural.
    Gera fluxogramas visuais em Mermaid.

    Usa HelenaSemanticPlanner para interpretação semântica robusta.
    """

    CAMPOS_FLUXOGRAMA = [
        {
            "nome": "nome_processo",
            "tipo": "texto",
            "mensagem": "Oi 👋 Vamos mapear seu processo visualmente! Qual o nome dele?",
            "exemplo": "Ex: 'Solicitação de férias', 'Aprovação de compras'"
        },
        {
            "nome": "etapas",
            "tipo": "lista",
            "mensagem": "Perfeito! Agora me conta: quais são as principais etapas desse processo, do início ao fim?",
            "exemplo": "Ex: '1. Servidor preenche formulário, 2. Chefia imediata analisa, 3. RH valida'"
        },
        {
            "nome": "decisoes",
            "tipo": "lista",
            "mensagem": "Legal! Em quais momentos há decisões/bifurcações? (aprovado/rejeitado, sim/não)",
            "exemplo": "Ex: 'Após análise da chefia → aprovado ou devolvido'"
        },
        {
            "nome": "responsaveis",
            "tipo": "mapeamento",
            "mensagem": "Quem são os responsáveis por cada etapa?",
            "exemplo": "Ex: 'Etapa 1 → Servidor, Etapa 2 → Chefia, Etapa 3 → RH'"
        },
        {
            "nome": "sistemas",
            "tipo": "lista",
            "mensagem": "Quais sistemas são utilizados no processo?",
            "exemplo": "Ex: 'SEI, SIGEPE, SouGov'"
        },
        {
            "nome": "tempo_medio",
            "tipo": "texto",
            "mensagem": "Por último: quanto tempo costuma levar do início ao fim?",
            "exemplo": "Ex: '5 dias úteis', '2 semanas', '1 mês'"
        }
    ]

    def __init__(self, llm: ChatOpenAI | None = None, dados_pdf: Dict[str, Any] | None = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.planner = HelenaSemanticPlanner()
        self.dados_pdf = dados_pdf or {}

    # =========================================================================
    # SHIM DE COMPATIBILIDADE COM ORQUESTRADOR
    # =========================================================================

    def processar_mensagem(self, mensagem: str, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        """
        Método de compatibilidade com o orquestrador.

        Retorna: {'campo', 'valor', 'proxima_pergunta', 'completo', 'percentual', 'validacao_ok'}
        """
        contexto = self._init_contexto(estrutura_atual)
        bruto = self.processar(mensagem, contexto)
        return self._to_orchestrator(bruto, contexto)

    # =========================================================================
    # LÓGICA INTERNA (FORMATO SEMÂNTICO)
    # =========================================================================

    def processar(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do usuário usando interpretação semântica.

        Returns formato interno:
            {
                'acao': str,
                'texto': str,
                'payload': dict
            }
        """
        msg = mensagem.lower().strip()

        # Inicializa estrutura
        contexto.setdefault("dados_coletados", {})
        contexto.setdefault("campo_atual_idx", 0)

        # Pré-popula com dados do PDF se disponível
        if self.dados_pdf and not contexto["dados_coletados"]:
            self._importar_dados_pdf(contexto)

        # 👋 Boas-vindas (primeira interação)
        if contexto["campo_atual_idx"] == 0:
            if any(p in msg for p in ["oi", "olá", "começar", "iniciar", "start", "mapear"]):
                return {
                    "acao": "boas_vindas",
                    "texto": (
                        "Oi 👋 Sou a Helena! Vou te ajudar a mapear seu processo visualmente.\n\n"
                        "Vamos conversar naturalmente e no final eu gero um fluxograma bonitinho pra você.\n\n"
                        "Vou te perguntar sobre:\n"
                        "📋 Nome do processo\n"
                        "🔄 Etapas principais\n"
                        "❓ Pontos de decisão\n"
                        "👥 Responsáveis\n"
                        "💻 Sistemas utilizados\n"
                        "⏱️ Tempo médio\n\n"
                        "Bora começar?"
                    ),
                    "payload": {}
                }

        # Detecta confirmações de dados do PDF (sim, correto, ok, confirma)
        if any(p in msg for p in ["sim", "correto", "ok", "confirma", "isso", "exato", "perfeito"]):
            # Se era uma confirmação de PDF, não salva - apenas avança
            pass
        # Detecta ajustes/negações
        elif any(p in msg for p in ["não", "nao", "errado", "ajustar", "mudar"]):
            # Se quer ajustar, limpa o valor do PDF do campo atual
            if contexto["campo_atual_idx"] > 0:
                idx = contexto["campo_atual_idx"] - 1
                if idx < len(self.CAMPOS_FLUXOGRAMA):
                    campo_nome = self.CAMPOS_FLUXOGRAMA[idx]["nome"]
                    if campo_nome in contexto["dados_coletados"]:
                        del contexto["dados_coletados"][campo_nome]
        # Salva resposta normal
        elif contexto["campo_atual_idx"] > 0:
            self._salvar_resposta_contexto(mensagem, contexto)

        # Verifica se acabou
        total_campos = len(self.CAMPOS_FLUXOGRAMA)
        if contexto["campo_atual_idx"] >= total_campos:
            return {
                "acao": "finalizar",
                "texto": (
                    "✅ Perfeito! Coletei todas as informações.\n\n"
                    "Agora vou gerar seu fluxograma visual em Mermaid...\n"
                    "Segundinho!"
                ),
                "payload": {"dados_completos": contexto["dados_coletados"]}
            }

        # Próxima pergunta
        return self._proxima_pergunta(contexto)

    def _proxima_pergunta(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna próxima pergunta do fluxo"""

        idx = contexto["campo_atual_idx"]

        if idx < len(self.CAMPOS_FLUXOGRAMA):
            campo = self.CAMPOS_FLUXOGRAMA[idx]
            contexto["campo_atual_idx"] += 1

            # Verifica se já tem valor do PDF
            if campo["nome"] in contexto["dados_coletados"]:
                valor_existente = contexto["dados_coletados"][campo["nome"]]
                return {
                    "acao": "confirmar_pdf",
                    "texto": (
                        f"📄 Vi aqui no seu PDF que **{campo['nome']}** seria:\n"
                        f"**{valor_existente}**\n\n"
                        "Está correto ou quer ajustar?"
                    ),
                    "payload": {
                        "campo_nome": campo["nome"],
                        "valor_pdf": valor_existente
                    }
                }

            # Pergunta normal
            progresso = f"[{contexto['campo_atual_idx']}/{len(self.CAMPOS_FLUXOGRAMA)}]"
            mensagem_completa = f"{progresso} {campo['mensagem']}"

            if campo.get("exemplo"):
                mensagem_completa += f"\n\n💡 {campo['exemplo']}"

            return {
                "acao": "fazer_pergunta",
                "texto": mensagem_completa,
                "payload": {
                    "campo_nome": campo["nome"],
                    "campo_config": campo
                }
            }

        # Acabou
        return {
            "acao": "finalizar",
            "texto": "✅ Dados completos! Gerando fluxograma...",
            "payload": {}
        }

    def _salvar_resposta_contexto(self, mensagem: str, contexto: Dict[str, Any]):
        """Salva resposta do usuário no contexto"""

        idx = contexto["campo_atual_idx"] - 1

        if idx < 0 or idx >= len(self.CAMPOS_FLUXOGRAMA):
            return

        campo = self.CAMPOS_FLUXOGRAMA[idx]
        nome_campo = campo["nome"]
        tipo_campo = campo["tipo"]

        # Normaliza conforme tipo
        if tipo_campo == "lista":
            # Detecta lista separada por vírgulas, números, ou quebras de linha
            itens = self._extrair_lista(mensagem)
            contexto["dados_coletados"][nome_campo] = itens

        elif tipo_campo == "mapeamento":
            # Tenta extrair mapeamento (Etapa X → Responsável Y)
            mapeamento = self._extrair_mapeamento(mensagem)
            contexto["dados_coletados"][nome_campo] = mapeamento

        elif tipo_campo == "texto":
            contexto["dados_coletados"][nome_campo] = mensagem.strip()

    def _extrair_lista(self, texto: str) -> List[str]:
        """Extrai lista de itens do texto"""
        # Remove numeração (1., 2., etc.)
        texto_limpo = re.sub(r'^\d+[\.)]\s*', '', texto, flags=re.MULTILINE)

        # Separa por vírgulas, quebras de linha ou ponto-e-vírgula
        itens = re.split(r'[,;\n]+', texto_limpo)

        # Limpa e filtra vazios
        itens_limpos = [item.strip() for item in itens if item.strip()]

        return itens_limpos if itens_limpos else [texto.strip()]

    def _extrair_mapeamento(self, texto: str) -> Dict[str, str]:
        """Extrai mapeamento etapa → responsável"""
        mapeamento = {}

        # Padrão: "Etapa X → Responsável" ou "Etapa X: Responsável"
        linhas = texto.split('\n')

        for linha in linhas:
            # Tenta capturar "Etapa/Step X → Y" ou "X: Y"
            match = re.search(r'(.+?)(?:→|:|-)\s*(.+)', linha)
            if match:
                chave = match.group(1).strip()
                valor = match.group(2).strip()
                mapeamento[chave] = valor

        # Se não encontrou nada estruturado, retorna texto bruto
        if not mapeamento:
            return {"geral": texto.strip()}

        return mapeamento

    def _importar_dados_pdf(self, contexto: Dict[str, Any]):
        """Importa dados extraídos do PDF do POP"""

        if not self.dados_pdf:
            return

        dados = contexto["dados_coletados"]

        # Nome do processo
        if self.dados_pdf.get('atividade') or self.dados_pdf.get('titulo'):
            dados['nome_processo'] = self.dados_pdf.get('atividade') or self.dados_pdf.get('titulo')

        # Sistemas utilizados
        if self.dados_pdf.get('sistemas'):
            dados['sistemas'] = self.dados_pdf.get('sistemas')

        # Responsáveis/Operadores
        if self.dados_pdf.get('operadores'):
            dados['responsaveis'] = {f"Etapa {i+1}": op for i, op in enumerate(self.dados_pdf.get('operadores'))}

    # =========================================================================
    # GERADOR DE FLUXOGRAMA MERMAID
    # =========================================================================

    def gerar_mermaid(self, dados: Dict[str, Any]) -> str:
        """Gera código Mermaid para fluxograma visual"""

        mermaid = "graph TD\n"

        nome_processo = dados.get('nome_processo', 'Processo')
        mermaid += f"    A[Início: {nome_processo}]\n"

        # Adicionar etapas
        etapas = dados.get('etapas', [])
        decisoes = dados.get('decisoes', [])

        for i, etapa in enumerate(etapas, start=1):
            letra = chr(65 + i)  # B, C, D...

            # Verifica se é ponto de decisão
            is_decisao = any(decisao.lower() in etapa.lower() for decisao in decisoes)

            if is_decisao:
                mermaid += f"    {letra}{{{{{etapa}}}}}\n"  # Losango
            else:
                mermaid += f"    {letra}[{etapa}]\n"  # Retângulo

        # Conectar etapas
        for i in range(len(etapas)):
            letra_atual = chr(65 + i)
            letra_prox = chr(65 + i + 1)
            mermaid += f"    {letra_atual} --> {letra_prox}\n"

        # Adicionar fim
        letra_fim = chr(65 + len(etapas) + 1)
        mermaid += f"    {chr(65 + len(etapas))} --> {letra_fim}[Fim]\n"

        # Adicionar metadata como comentário
        mermaid += f"\n%% Sistemas: {', '.join(dados.get('sistemas', []))}\n"
        mermaid += f"%% Tempo médio: {dados.get('tempo_medio', 'Não informado')}\n"

        return mermaid

    # =========================================================================
    # CONVERSORES DE FORMATO
    # =========================================================================

    def _init_contexto(self, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        """Inicializa contexto a partir da estrutura do orquestrador."""
        ctx = copy.deepcopy(estrutura_atual or {})
        ctx.setdefault("dados_coletados", {})
        ctx.setdefault("campo_atual_idx", 0)
        return ctx

    def _to_orchestrator(self, bruto: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte formato interno {acao, texto, payload} para contrato do orquestrador.
        """
        acao = bruto.get("acao")
        texto = bruto.get("texto", "")
        payload = bruto.get("payload", {})

        # Mapeamento de ações → campo/valor
        mapeamento = {
            "boas_vindas": ("inicio", None, True),
            "fazer_pergunta": ("pergunta", payload.get("campo_nome"), True),
            "confirmar_pdf": ("confirmar_pdf", payload.get("valor_pdf"), True),
            "finalizar": ("fluxograma", payload.get("dados_completos"), True),
        }

        campo, valor, validacao_ok = mapeamento.get(acao, ("neutro", None, True))

        return {
            "campo": campo,
            "valor": valor,
            "proxima_pergunta": texto,
            "completo": acao == "finalizar",
            "percentual": self._calc_percentual(contexto),
            "validacao_ok": validacao_ok
        }

    def _calc_percentual(self, contexto: Dict[str, Any]) -> int:
        """Calcula percentual de conclusão do mapeamento."""
        idx = contexto.get("campo_atual_idx", 0)
        total = len(self.CAMPOS_FLUXOGRAMA)

        if idx == 0:
            return 5

        percentual = int((idx / total) * 95) + 5
        return min(percentual, 100)


# Alias para compatibilidade
HelenaFlowchartAgent = FlowchartAgent
