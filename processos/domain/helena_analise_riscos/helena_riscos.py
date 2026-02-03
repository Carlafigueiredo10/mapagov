"""
Helena Riscos - Agente Conversacional para Analise de Riscos

Guia o usuario atraves das 6 etapas da analise de riscos:
1. Contextualizacao (questionario inicial)
2. Identificacao de riscos
3. Analise de probabilidade e impacto
4. Avaliacao (matriz 5x5)
5. Resposta ao risco
6. Finalizacao e documentacao
"""
import logging
from typing import List

from processos.domain.base import BaseHelena
from processos.domain.helena_analise_riscos.enums import (
    CategoriaRisco,
    EstrategiaResposta,
)
from processos.domain.helena_analise_riscos.matriz import (
    calcular_score,
    calcular_nivel,
    get_cor_nivel,
)
from processos.domain.helena_analise_riscos.constants import (
    AREAS_DECIPEX,
    DESCRICOES_CATEGORIA,
    DESCRICOES_ESTRATEGIA,
)

logger = logging.getLogger(__name__)


# Etapas do fluxo de analise de riscos
ETAPAS_ANALISE = {
    1: {"nome": "Contextualizacao", "descricao": "Definir area e macroprocesso"},
    2: {"nome": "Identificacao", "descricao": "Identificar riscos potenciais"},
    3: {"nome": "Analise", "descricao": "Avaliar probabilidade e impacto"},
    4: {"nome": "Avaliacao", "descricao": "Visualizar matriz de riscos"},
    5: {"nome": "Resposta", "descricao": "Definir estrategias de resposta"},
    6: {"nome": "Finalizacao", "descricao": "Revisar e documentar"},
}


class HelenaRiscos(BaseHelena):
    """
    Helena Riscos - Produto conversacional para analise de riscos.

    Guia o usuario atraves do processo de identificacao,
    analise e resposta a riscos de forma conversacional.
    """

    VERSION = "1.0.0"
    PRODUTO_NOME = "Helena Riscos"

    def __init__(self):
        super().__init__()

    def inicializar_estado(self) -> dict:
        """
        Retorna estado inicial para Helena Riscos.

        Returns:
            dict: Estado inicial com etapa 1 e dados vazios
        """
        return {
            "etapa_atual": 1,
            "analise_id": None,
            "questoes_respondidas": {},
            "area_decipex": None,
            "riscos_identificados": [],
            "historico": [],
            "contador_mensagens": 0,
        }

    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa mensagem do usuario na etapa atual.

        Args:
            mensagem: Texto do usuario
            session_data: Estado atual da sessao

        Returns:
            dict: Resposta com novo estado
        """
        self.validar_mensagem(mensagem)
        self.validar_session_data(session_data)

        etapa = session_data.get("etapa_atual", 1)
        session_data["contador_mensagens"] += 1

        # Adicionar ao historico
        session_data["historico"].append({
            "role": "user",
            "content": mensagem,
            "etapa": etapa,
        })

        # Processar por etapa
        if etapa == 1:
            resultado = self._processar_contextualizacao(mensagem, session_data)
        elif etapa == 2:
            resultado = self._processar_identificacao(mensagem, session_data)
        elif etapa == 3:
            resultado = self._processar_analise(mensagem, session_data)
        elif etapa == 4:
            resultado = self._processar_avaliacao(mensagem, session_data)
        elif etapa == 5:
            resultado = self._processar_resposta(mensagem, session_data)
        elif etapa == 6:
            resultado = self._processar_finalizacao(mensagem, session_data)
        else:
            resultado = self._criar_resposta_erro("Etapa invalida", session_data)

        # Adicionar resposta ao historico
        session_data["historico"].append({
            "role": "assistant",
            "content": resultado.get("resposta", ""),
            "etapa": session_data.get("etapa_atual", etapa),
        })

        return resultado

    # =========================================================================
    # ETAPA 1: CONTEXTUALIZACAO
    # =========================================================================

    def _processar_contextualizacao(
        self, mensagem: str, session_data: dict
    ) -> dict:
        """Processa etapa de contextualizacao (questionario)"""
        msg_lower = mensagem.lower().strip()

        # Verificar se usuario selecionou area DECIPEX
        for codigo, nome in AREAS_DECIPEX.items():
            if codigo.lower() in msg_lower or nome.lower() in msg_lower:
                session_data["area_decipex"] = codigo
                session_data["questoes_respondidas"]["Q_CONTEXTO_01"] = codigo

                resposta = (
                    f"Otimo! Area {codigo} ({nome}) selecionada. "
                    f"Agora vamos para a identificacao de riscos. "
                    f"Descreva o processo ou atividade que deseja analisar."
                )
                session_data["etapa_atual"] = 2

                return self.criar_resposta(
                    resposta=resposta,
                    novo_estado=session_data,
                    progresso="1/6 etapas",
                )

        # Mensagem inicial ou sem selecao valida
        areas_texto = "\n".join(
            f"- {codigo}: {nome}" for codigo, nome in AREAS_DECIPEX.items()
        )
        resposta = (
            "Ola! Sou a Helena e vou ajuda-lo na analise de riscos.\n\n"
            "Primeiro, selecione a area DECIPEX responsavel:\n"
            f"{areas_texto}\n\n"
            "Digite o codigo ou nome da area."
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="1/6 etapas",
            tipo_interface="selecao_area",
            dados_interface={"areas": AREAS_DECIPEX},
        )

    # =========================================================================
    # ETAPA 2: IDENTIFICACAO
    # =========================================================================

    def _processar_identificacao(
        self, mensagem: str, session_data: dict
    ) -> dict:
        """Processa etapa de identificacao de riscos"""
        msg_lower = mensagem.lower().strip()

        # Verificar comandos de navegacao
        if "avancar" in msg_lower or "proximo" in msg_lower or "continuar" in msg_lower:
            if not session_data.get("riscos_identificados"):
                return self.criar_resposta(
                    resposta="Voce ainda nao identificou nenhum risco. Descreva pelo menos um risco antes de avancar.",
                    novo_estado=session_data,
                    progresso="2/6 etapas",
                )
            session_data["etapa_atual"] = 3
            return self._iniciar_etapa_analise(session_data)

        # Sugerir riscos com base nas categorias
        categorias_texto = "\n".join(
            f"- {cat.value}: {DESCRICOES_CATEGORIA.get(cat.value, '')}"
            for cat in CategoriaRisco
        )

        # Processar risco mencionado pelo usuario
        if len(mensagem) > 10:  # Mensagem substancial
            novo_risco = {
                "titulo": mensagem[:100],
                "categoria": self._inferir_categoria(mensagem),
                "descricao": mensagem,
                "probabilidade": None,
                "impacto": None,
            }
            session_data["riscos_identificados"].append(novo_risco)

            qtd = len(session_data["riscos_identificados"])
            resposta = (
                f"Risco registrado! Voce tem {qtd} risco(s) identificado(s).\n\n"
                "Deseja adicionar mais riscos ou avancar para analise?\n"
                "(Digite 'avancar' para ir para a proxima etapa)"
            )

            return self.criar_resposta(
                resposta=resposta,
                novo_estado=session_data,
                progresso="2/6 etapas",
                tipo_interface="lista_riscos",
                dados_interface={"riscos": session_data["riscos_identificados"]},
            )

        # Pedir mais informacoes
        resposta = (
            "Descreva os riscos que identificou para este processo.\n\n"
            f"Categorias disponiveis:\n{categorias_texto}\n\n"
            "Exemplo: 'Falha no sistema de pagamentos pode causar atraso nos beneficios'"
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="2/6 etapas",
        )

    def _inferir_categoria(self, texto: str) -> str:
        """Infere categoria do risco com base em palavras-chave"""
        texto_lower = texto.lower()

        mapa_palavras = {
            "FINANCEIRO": ["orcamento", "custo", "financeiro", "pagamento", "verba"],
            "LEGAL": ["lei", "norma", "regulamento", "compliance", "juridico", "legal"],
            "TECNOLOGICO": ["sistema", "ti", "tecnologia", "software", "dados"],
            "REPUTACIONAL": ["imagem", "reputacao", "midia", "publico"],
            "IMPACTO_DESIGUAL": ["desigual", "vulneravel", "discrimina", "equidade"],
        }

        for categoria, palavras in mapa_palavras.items():
            if any(p in texto_lower for p in palavras):
                return categoria

        return "OPERACIONAL"  # Default

    # =========================================================================
    # ETAPA 3: ANALISE
    # =========================================================================

    def _processar_analise(
        self, mensagem: str, session_data: dict
    ) -> dict:
        """Processa etapa de analise (probabilidade e impacto)"""
        msg_lower = mensagem.lower().strip()

        # Verificar comando de avanco
        if "avancar" in msg_lower or "proximo" in msg_lower:
            # Verificar se todos os riscos foram analisados
            todos_analisados = all(
                r.get("probabilidade") and r.get("impacto")
                for r in session_data.get("riscos_identificados", [])
            )
            if not todos_analisados:
                return self.criar_resposta(
                    resposta="Ainda ha riscos sem probabilidade/impacto definidos. Complete a analise antes de avancar.",
                    novo_estado=session_data,
                    progresso="3/6 etapas",
                )
            session_data["etapa_atual"] = 4
            return self._iniciar_etapa_avaliacao(session_data)

        # Processar valores de probabilidade/impacto
        digitos = [int(c) for c in mensagem if c.isdigit()]
        numeros = [n for n in digitos if 1 <= n <= 5]

        if len(numeros) >= 2:
            # Encontrar risco sem analise
            for risco in session_data["riscos_identificados"]:
                if not risco.get("probabilidade"):
                    risco["probabilidade"] = numeros[0]
                    risco["impacto"] = numeros[1]
                    risco["score"] = calcular_score(numeros[0], numeros[1])
                    risco["nivel"] = calcular_nivel(risco["score"])
                    break

            return self._mostrar_progresso_analise(session_data)

        return self._iniciar_etapa_analise(session_data)

    def _iniciar_etapa_analise(self, session_data: dict) -> dict:
        """Mostra instrucoes para analise de riscos"""
        riscos = session_data.get("riscos_identificados", [])
        sem_analise = [r for r in riscos if not r.get("probabilidade")]

        if not sem_analise:
            session_data["etapa_atual"] = 4
            return self._iniciar_etapa_avaliacao(session_data)

        risco_atual = sem_analise[0]
        resposta = (
            f"Analise do risco: '{risco_atual['titulo'][:50]}...'\n\n"
            "Informe PROBABILIDADE e IMPACTO (1-5):\n"
            "- 1: Muito baixo\n"
            "- 2: Baixo\n"
            "- 3: Medio\n"
            "- 4: Alto\n"
            "- 5: Muito alto\n\n"
            "Exemplo: '3 4' (probabilidade 3, impacto 4)"
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="3/6 etapas",
            tipo_interface="matriz_input",
            dados_interface={"risco": risco_atual},
        )

    def _mostrar_progresso_analise(self, session_data: dict) -> dict:
        """Mostra progresso da analise de riscos"""
        riscos = session_data.get("riscos_identificados", [])
        analisados = [r for r in riscos if r.get("probabilidade")]
        sem_analise = [r for r in riscos if not r.get("probabilidade")]

        if sem_analise:
            return self._iniciar_etapa_analise(session_data)

        resposta = (
            f"Todos os {len(riscos)} riscos foram analisados!\n\n"
            "Digite 'avancar' para ver a matriz de riscos."
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="3/6 etapas",
            tipo_interface="lista_riscos_analisados",
            dados_interface={"riscos": analisados},
        )

    # =========================================================================
    # ETAPA 4: AVALIACAO
    # =========================================================================

    def _processar_avaliacao(
        self, mensagem: str, session_data: dict
    ) -> dict:
        """Processa etapa de avaliacao (matriz)"""
        msg_lower = mensagem.lower().strip()

        if "avancar" in msg_lower or "proximo" in msg_lower or "continuar" in msg_lower:
            session_data["etapa_atual"] = 5
            return self._iniciar_etapa_resposta(session_data)

        return self._iniciar_etapa_avaliacao(session_data)

    def _iniciar_etapa_avaliacao(self, session_data: dict) -> dict:
        """Mostra matriz de riscos"""
        riscos = session_data.get("riscos_identificados", [])

        # Preparar dados da matriz
        matriz_dados = []
        for r in riscos:
            if r.get("score"):
                matriz_dados.append({
                    "titulo": r["titulo"][:30],
                    "probabilidade": r["probabilidade"],
                    "impacto": r["impacto"],
                    "score": r["score"],
                    "nivel": r["nivel"],
                    "cor": get_cor_nivel(r["nivel"]),
                })

        # Contar por nivel
        contagem = {}
        for r in matriz_dados:
            nivel = r["nivel"]
            contagem[nivel] = contagem.get(nivel, 0) + 1

        resumo = ", ".join(f"{n}: {c}" for n, c in contagem.items())

        resposta = (
            f"Matriz de Riscos (5x5)\n\n"
            f"Total: {len(matriz_dados)} riscos\n"
            f"Distribuicao: {resumo}\n\n"
            "Analise os riscos na matriz e digite 'avancar' para definir respostas."
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="4/6 etapas",
            tipo_interface="matriz_riscos",
            dados_interface={"riscos": matriz_dados, "contagem": contagem},
        )

    # =========================================================================
    # ETAPA 5: RESPOSTA
    # =========================================================================

    def _processar_resposta(
        self, mensagem: str, session_data: dict
    ) -> dict:
        """Processa etapa de resposta ao risco"""
        msg_lower = mensagem.lower().strip()

        if "avancar" in msg_lower or "finalizar" in msg_lower:
            session_data["etapa_atual"] = 6
            return self._iniciar_etapa_finalizacao(session_data)

        # Detectar estrategia mencionada
        for estrategia in EstrategiaResposta:
            if estrategia.value.lower() in msg_lower:
                # Encontrar risco sem resposta
                for risco in session_data["riscos_identificados"]:
                    if not risco.get("estrategia"):
                        risco["estrategia"] = estrategia.value
                        risco["acao_resposta"] = mensagem
                        break

                return self._mostrar_progresso_resposta(session_data)

        return self._iniciar_etapa_resposta(session_data)

    def _iniciar_etapa_resposta(self, session_data: dict) -> dict:
        """Mostra opcoes de resposta ao risco"""
        riscos = session_data.get("riscos_identificados", [])
        sem_resposta = [r for r in riscos if not r.get("estrategia")]

        if not sem_resposta:
            session_data["etapa_atual"] = 6
            return self._iniciar_etapa_finalizacao(session_data)

        risco_atual = sem_resposta[0]
        estrategias_texto = "\n".join(
            f"- {e.value}: {DESCRICOES_ESTRATEGIA.get(e.value, '')}"
            for e in EstrategiaResposta
        )

        resposta = (
            f"Risco: '{risco_atual['titulo'][:50]}...'\n"
            f"Nivel: {risco_atual.get('nivel', 'N/A')} (score {risco_atual.get('score', 0)})\n\n"
            f"Estrategias disponiveis:\n{estrategias_texto}\n\n"
            "Escolha uma estrategia e descreva a acao."
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="5/6 etapas",
            tipo_interface="estrategia_resposta",
            dados_interface={
                "risco": risco_atual,
                "estrategias": [e.value for e in EstrategiaResposta],
            },
        )

    def _mostrar_progresso_resposta(self, session_data: dict) -> dict:
        """Mostra progresso das respostas definidas"""
        riscos = session_data.get("riscos_identificados", [])
        sem_resposta = [r for r in riscos if not r.get("estrategia")]

        if sem_resposta:
            return self._iniciar_etapa_resposta(session_data)

        resposta = (
            f"Todas as respostas foram definidas!\n\n"
            "Digite 'finalizar' para revisar e concluir a analise."
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="5/6 etapas",
        )

    # =========================================================================
    # ETAPA 6: FINALIZACAO
    # =========================================================================

    def _processar_finalizacao(
        self, mensagem: str, session_data: dict
    ) -> dict:
        """Processa etapa de finalizacao"""
        msg_lower = mensagem.lower().strip()

        if "confirmar" in msg_lower or "concluir" in msg_lower or "finalizar" in msg_lower:
            return self._concluir_analise(session_data)

        return self._iniciar_etapa_finalizacao(session_data)

    def _iniciar_etapa_finalizacao(self, session_data: dict) -> dict:
        """Mostra resumo para finalizacao"""
        riscos = session_data.get("riscos_identificados", [])

        resumo_riscos = []
        for r in riscos:
            resumo_riscos.append({
                "titulo": r["titulo"][:50],
                "categoria": r.get("categoria", "N/A"),
                "nivel": r.get("nivel", "N/A"),
                "estrategia": r.get("estrategia", "N/A"),
            })

        resposta = (
            "Resumo da Analise de Riscos\n\n"
            f"Area: {session_data.get('area_decipex', 'N/A')}\n"
            f"Total de riscos: {len(riscos)}\n\n"
            "Revise os dados acima e digite 'confirmar' para finalizar."
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="6/6 etapas",
            tipo_interface="resumo_analise",
            dados_interface={
                "area": session_data.get("area_decipex"),
                "riscos": resumo_riscos,
                "total": len(riscos),
            },
        )

    def _concluir_analise(self, session_data: dict) -> dict:
        """Conclui a analise de riscos"""
        riscos = session_data.get("riscos_identificados", [])

        resposta = (
            "Analise de riscos finalizada com sucesso!\n\n"
            f"Total de riscos documentados: {len(riscos)}\n\n"
            "Os dados foram salvos e estao disponiveis para consulta."
        )

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="Concluido",
            tipo_interface="analise_concluida",
            dados_interface={
                "analise_id": session_data.get("analise_id"),
                "total_riscos": len(riscos),
            },
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _detectar_comando_navegacao(self, mensagem: str) -> bool:
        """Detecta se usuario quer avancar para proxima etapa"""
        msg_lower = mensagem.lower().strip()
        comandos = ["avancar", "proximo", "continuar", "finalizar", "confirmar", "concluir"]
        return any(cmd in msg_lower for cmd in comandos)

    def _criar_resposta_erro(self, erro: str, session_data: dict) -> dict:
        """Cria resposta de erro padronizada"""
        return self.criar_resposta(
            resposta=f"Erro: {erro}",
            novo_estado=session_data,
        )

    def get_etapas(self) -> dict:
        """Retorna definicao das etapas"""
        return ETAPAS_ANALISE

    def get_categorias(self) -> List[str]:
        """Retorna lista de categorias de risco"""
        return [c.value for c in CategoriaRisco]

    def get_estrategias(self) -> List[str]:
        """Retorna lista de estrategias de resposta"""
        return [e.value for e in EstrategiaResposta]
