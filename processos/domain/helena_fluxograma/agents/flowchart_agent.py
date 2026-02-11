"""
Helena Flowchart Agent - gera fluxogramas a partir de etapas e decisões.

Fase 1: Coleta etapas e decisões (via PDF ou descrição manual)
Fase 2: Edição pós-geração via comandos simples com IDs estáveis
"""

from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger("helena_flowchart_agent")


class FlowchartAgent:

    CAMPOS_FLUXOGRAMA = [
        {
            "nome": "etapas",
            "mensagem": "Quais são as etapas do processo, do início ao fim?",
            "exemplo": "Ex: 1. Servidor preenche formulário, 2. Chefia analisa, 3. RH valida",
        },
        {
            "nome": "decisoes",
            "mensagem": (
                "Há pontos de decisão ou bifurcação no processo?\n"
                "(Pode dizer 'não' se o fluxo for linear)"
            ),
            "exemplo": "Ex: Após etapa 2: Aprovado? sim->3 não->1",
        },
    ]

    def __init__(self, dados_pdf: Dict[str, Any] | None = None):
        self.dados_pdf = dados_pdf or {}

    # =========================================================================
    # INTERFACE COM ORQUESTRADOR
    # =========================================================================

    def processar_mensagem(self, mensagem: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entry point chamado pelo orquestrador.

        Retorna: {proxima_pergunta, completo, percentual, validacao_ok}
        """
        ctx = self._init_contexto(session_data)

        if ctx.get("fluxograma_gerado"):
            return self._processar_edicao(mensagem, ctx)

        return self._processar_coleta(mensagem, ctx)

    # =========================================================================
    # FASE 1 — COLETA (etapas + decisões)
    # =========================================================================

    def _processar_coleta(self, mensagem: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        msg = mensagem.lower().strip()
        idx = ctx["campo_atual_idx"]

        # Importa metadata do PDF uma única vez
        if not ctx.get("pdf_importado") and self.dados_pdf:
            self._importar_dados_pdf(ctx)
            ctx["pdf_importado"] = True

        # Primeira interação — qualquer mensagem inicia a conversa
        if idx == 0:
            nome = ctx.get("nome_processo", "seu processo")
            prefixo = (
                f"Vamos mapear o fluxograma de **{nome}**.\n\n"
                "Preciso de duas coisas:\n"
                "1. As etapas do processo (do início ao fim)\n"
                "2. Os pontos de decisão (se houver)\n\n"
            )
            return self._fazer_pergunta(ctx, texto_prefixo=prefixo)

        # Salva resposta do campo anterior
        if idx > 0 and idx <= len(self.CAMPOS_FLUXOGRAMA):
            campo = self.CAMPOS_FLUXOGRAMA[idx - 1]
            if campo["nome"] == "etapas":
                self._salvar_etapas(mensagem, ctx)
            elif campo["nome"] == "decisoes":
                self._salvar_decisoes(mensagem, ctx)

        # Verifica se coletou tudo
        if ctx["campo_atual_idx"] >= len(self.CAMPOS_FLUXOGRAMA):
            ctx["fluxograma_gerado"] = True
            logger.info("[coleta] completo → gerando fluxograma")

            guia = (
                "\n\nPode editar o fluxograma com comandos:\n"
                "- `editar etapa N: novo texto`\n"
                "- `inserir etapa após N: texto`\n"
                "- `remover etapa N`\n"
                "- `inserir decisão após N: Condição? sim->X não->Y`"
            )
            return {
                "proxima_pergunta": "Fluxograma gerado!" + guia,
                "completo": True,
                "percentual": 100,
                "validacao_ok": True,
            }

        return self._fazer_pergunta(ctx)

    def _fazer_pergunta(
        self, ctx: Dict[str, Any], texto_prefixo: str = ""
    ) -> Dict[str, Any]:
        idx = ctx["campo_atual_idx"]

        if idx >= len(self.CAMPOS_FLUXOGRAMA):
            return {
                "proxima_pergunta": "Algo deu errado. Tente novamente.",
                "completo": False,
                "percentual": 0,
                "validacao_ok": False,
            }

        campo = self.CAMPOS_FLUXOGRAMA[idx]
        ctx["campo_atual_idx"] += 1
        logger.info(f"[coleta] campo_atual_idx → {ctx['campo_atual_idx']}")

        progresso = f"[{ctx['campo_atual_idx']}/{len(self.CAMPOS_FLUXOGRAMA)}]"
        texto = f"{texto_prefixo}{progresso} {campo['mensagem']}\n\n{campo['exemplo']}"

        return {
            "proxima_pergunta": texto,
            "completo": False,
            "percentual": self._calc_percentual(ctx),
            "validacao_ok": True,
        }

    # ---- salvar respostas ----

    def _salvar_etapas(self, texto: str, ctx: Dict[str, Any]):
        itens = self._extrair_lista(texto)
        etapas = []
        for i, item in enumerate(itens, start=1):
            etapas.append({"id": i, "texto": item})
        ctx["etapas"] = etapas
        ctx["proximo_etapa_id"] = len(etapas) + 1
        logger.info(f"[etapas] {len(etapas)} etapas salvas")

    def _salvar_decisoes(self, texto: str, ctx: Dict[str, Any]):
        msg = texto.lower().strip()

        sem_decisao = [
            "não", "nao", "nenhuma", "nenhum", "sem decisão", "sem decisao",
            "linear", "nao tem", "não tem", "n", "nope",
        ]
        if any(p in msg for p in sem_decisao):
            ctx["decisoes"] = []
            ctx["proximo_decisao_id"] = 1
            logger.info("[decisoes] Fluxo linear (sem decisões)")
            return

        decisoes = self._parse_decisoes(texto, ctx)
        ctx["decisoes"] = decisoes
        ctx["proximo_decisao_id"] = len(decisoes) + 1
        logger.info(f"[decisoes] {len(decisoes)} decisão(ões) salva(s)")

    def _parse_decisoes(
        self, texto: str, ctx: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Tenta parse estruturado:  Após etapa N: Condição? sim->X não->Y
        Fallback: texto bruto com defaults razoáveis.
        """
        etapas = ctx.get("etapas", [])
        etapa_ids = [e["id"] for e in etapas]
        decisoes: List[Dict[str, Any]] = []
        linhas = re.split(r"[;\n]+", texto)
        did = 1

        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue

            # Padrão completo: "Após etapa 2: Aprovado? sim->3 não->1"
            m = re.match(
                r"(?:ap[oó]s\s+(?:etapa\s+)?)?(\d+)\s*[:]\s*"
                r"(.+?)\?\s*sim\s*->\s*(\d+)\s*[,;]?\s*n[aã]o\s*->\s*(\d+)",
                linha,
                re.IGNORECASE,
            )
            if m:
                apos = int(m.group(1))
                decisoes.append({
                    "id": did,
                    "apos_etapa_id": apos if apos in etapa_ids else etapa_ids[-1],
                    "condicao": m.group(2).strip() + "?",
                    "sim_id": int(m.group(3)),
                    "nao_id": int(m.group(4)),
                })
                did += 1
                continue

            # Padrão sem "após": "Aprovado? sim->3 não->1"
            m2 = re.match(
                r"(.+?)\?\s*sim\s*->\s*(\d+)\s*[,;]?\s*n[aã]o\s*->\s*(\d+)",
                linha,
                re.IGNORECASE,
            )
            if m2:
                apos = etapa_ids[min(did, len(etapa_ids)) - 1] if etapa_ids else 1
                decisoes.append({
                    "id": did,
                    "apos_etapa_id": apos,
                    "condicao": m2.group(1).strip() + "?",
                    "sim_id": int(m2.group(2)),
                    "nao_id": int(m2.group(3)),
                })
                did += 1
                continue

            # Fallback: texto natural → decisão no ponto médio do fluxo
            if len(etapa_ids) >= 2:
                mid = len(etapa_ids) // 2
                decisoes.append({
                    "id": did,
                    "apos_etapa_id": etapa_ids[mid],
                    "condicao": linha.rstrip("?") + "?",
                    "sim_id": etapa_ids[min(mid + 1, len(etapa_ids) - 1)],
                    "nao_id": etapa_ids[max(mid - 1, 0)],
                })
                did += 1

        return decisoes

    # =========================================================================
    # FASE 2 — EDIÇÃO PÓS-GERAÇÃO
    # =========================================================================

    def _processar_edicao(self, mensagem: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        cmd = self._parse_comando(mensagem.strip())

        if not cmd:
            return {
                "proxima_pergunta": (
                    "Não entendi o comando. Tente:\n"
                    "- `editar etapa N: novo texto`\n"
                    "- `inserir etapa após N: texto`\n"
                    "- `remover etapa N`\n"
                    "- `inserir decisão após N: Condição? sim->X não->Y`"
                ),
                "completo": True,
                "percentual": 100,
                "validacao_ok": True,
            }

        resultado = self._executar_comando(cmd, ctx)

        return {
            "proxima_pergunta": resultado.get("erro") or resultado["mensagem"],
            "completo": True,
            "percentual": 100,
            "validacao_ok": "erro" not in resultado,
        }

    def _parse_comando(self, msg: str) -> Optional[Dict[str, Any]]:
        # editar etapa N: TEXTO
        m = re.match(r"editar\s+etapa\s+(\d+)\s*:\s*(.+)", msg, re.IGNORECASE)
        if m:
            return {"tipo": "editar_etapa", "id": int(m.group(1)), "texto": m.group(2).strip()}

        # inserir etapa após N: TEXTO
        m = re.match(r"inserir\s+etapa\s+ap[oó]s\s+(\d+)\s*:\s*(.+)", msg, re.IGNORECASE)
        if m:
            return {"tipo": "inserir_etapa", "apos_id": int(m.group(1)), "texto": m.group(2).strip()}

        # remover etapa N
        m = re.match(r"remover\s+etapa\s+(\d+)", msg, re.IGNORECASE)
        if m:
            return {"tipo": "remover_etapa", "id": int(m.group(1))}

        # inserir decisão após N: COND? sim->X não->Y
        m = re.match(
            r"inserir\s+decis[aã]o\s+ap[oó]s\s+(\d+)\s*:\s*"
            r"(.+?)\?\s*sim\s*->\s*(\d+)\s*[,;]?\s*n[aã]o\s*->\s*(\d+)",
            msg,
            re.IGNORECASE,
        )
        if m:
            return {
                "tipo": "inserir_decisao",
                "apos_id": int(m.group(1)),
                "condicao": m.group(2).strip() + "?",
                "sim_id": int(m.group(3)),
                "nao_id": int(m.group(4)),
            }

        # remover decisão N
        m = re.match(r"remover\s+decis[aã]o\s+(\d+)", msg, re.IGNORECASE)
        if m:
            return {"tipo": "remover_decisao", "id": int(m.group(1))}

        return None

    def _executar_comando(self, cmd: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        etapas = ctx.get("etapas", [])
        decisoes = ctx.get("decisoes", [])
        etapa_ids = {e["id"] for e in etapas}
        tipo = cmd["tipo"]

        if tipo == "editar_etapa":
            target = next((e for e in etapas if e["id"] == cmd["id"]), None)
            if not target:
                return {"erro": f"Etapa {cmd['id']} não encontrada. IDs disponíveis: {sorted(etapa_ids)}"}
            old = target["texto"]
            target["texto"] = cmd["texto"]
            logger.info(f"[editar] Etapa {cmd['id']}: '{old}' → '{cmd['texto']}'")
            return {"mensagem": f"Etapa {cmd['id']} atualizada."}

        if tipo == "inserir_etapa":
            if cmd["apos_id"] not in etapa_ids:
                return {"erro": f"Etapa {cmd['apos_id']} não encontrada. IDs: {sorted(etapa_ids)}"}
            novo_id = ctx.get("proximo_etapa_id", max(etapa_ids, default=0) + 1)
            pos = next(i for i, e in enumerate(etapas) if e["id"] == cmd["apos_id"])
            etapas.insert(pos + 1, {"id": novo_id, "texto": cmd["texto"]})
            ctx["proximo_etapa_id"] = novo_id + 1
            logger.info(f"[inserir] Etapa {novo_id} após {cmd['apos_id']}")
            return {"mensagem": f"Etapa {novo_id} inserida após etapa {cmd['apos_id']}."}

        if tipo == "remover_etapa":
            target = next((e for e in etapas if e["id"] == cmd["id"]), None)
            if not target:
                return {"erro": f"Etapa {cmd['id']} não encontrada. IDs: {sorted(etapa_ids)}"}
            refs = [
                d for d in decisoes
                if cmd["id"] in (d["sim_id"], d["nao_id"], d["apos_etapa_id"])
            ]
            if refs:
                ref_ids = [f"D{d['id']}" for d in refs]
                return {
                    "erro": (
                        f"Etapa {cmd['id']} é referenciada por decisão(ões) {', '.join(ref_ids)}. "
                        "Remova ou edite as decisões primeiro."
                    )
                }
            etapas.remove(target)
            logger.info(f"[remover] Etapa {cmd['id']}")
            return {"mensagem": f"Etapa {cmd['id']} removida."}

        if tipo == "inserir_decisao":
            for label, eid in [("após", cmd["apos_id"]), ("sim", cmd["sim_id"]), ("não", cmd["nao_id"])]:
                if eid not in etapa_ids:
                    return {"erro": f"Etapa destino {label}={eid} não encontrada. IDs: {sorted(etapa_ids)}"}
            novo_id = ctx.get("proximo_decisao_id", max((d["id"] for d in decisoes), default=0) + 1)
            decisoes.append({
                "id": novo_id,
                "apos_etapa_id": cmd["apos_id"],
                "condicao": cmd["condicao"],
                "sim_id": cmd["sim_id"],
                "nao_id": cmd["nao_id"],
            })
            ctx["proximo_decisao_id"] = novo_id + 1
            logger.info(f"[decisao] D{novo_id} após E{cmd['apos_id']}")
            return {"mensagem": f"Decisão {novo_id} inserida após etapa {cmd['apos_id']}."}

        if tipo == "remover_decisao":
            target = next((d for d in decisoes if d["id"] == cmd["id"]), None)
            if not target:
                ids_disp = sorted(d["id"] for d in decisoes)
                return {"erro": f"Decisão {cmd['id']} não encontrada. IDs: {ids_disp}"}
            decisoes.remove(target)
            logger.info(f"[remover] Decisão {cmd['id']}")
            return {"mensagem": f"Decisão {cmd['id']} removida."}

        return {"erro": "Comando não reconhecido."}

    # =========================================================================
    # GERADOR DE FLUXOGRAMA MERMAID
    # =========================================================================

    def gerar_mermaid(self, ctx: Dict[str, Any]) -> str:
        """Gera Mermaid a partir da estrutura interna (etapas + decisões)."""
        etapas = ctx.get("etapas", [])
        decisoes = ctx.get("decisoes", [])
        nome = self._sanitize(ctx.get("nome_processo", "Processo"))

        if not etapas:
            return "graph TD\n    inicio([Início]) --> fim([Fim])"

        # --- nós ---
        lines = ["graph TD"]
        lines.append(f"    inicio([Início: {nome}])")
        for e in etapas:
            txt = self._sanitize(e["texto"])
            lines.append(f'    e{e["id"]}["{e["id"]}. {txt}"]')
        for d in decisoes:
            cond = self._sanitize(d["condicao"])
            lines.append(f"    d{d['id']}{{{{{cond}}}}}")
        lines.append("    fim([Fim])")
        lines.append("")

        # --- arestas ---
        decisao_por_etapa: Dict[int, List[Dict]] = {}
        for d in decisoes:
            decisao_por_etapa.setdefault(d["apos_etapa_id"], []).append(d)

        # início → primeira etapa
        lines.append(f"    inicio --> e{etapas[0]['id']}")

        for i, e in enumerate(etapas):
            eid = e["id"]

            if eid in decisao_por_etapa:
                for d in decisao_por_etapa[eid]:
                    lines.append(f"    e{eid} --> d{d['id']}")
                    lines.append(f"    d{d['id']} -->|Sim| e{d['sim_id']}")
                    lines.append(f"    d{d['id']} -->|Não| e{d['nao_id']}")
            else:
                if i + 1 < len(etapas):
                    lines.append(f"    e{eid} --> e{etapas[i + 1]['id']}")
                else:
                    lines.append(f"    e{eid} --> fim")

        return "\n".join(lines)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _init_contexto(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inicializa contexto in-place (preserva referência do caller)."""
        # Reset sessões do formato antigo (antes da v3)
        if session_data.get("_version") != "3":
            session_data.clear()
            session_data["_version"] = "3"
        session_data.setdefault("campo_atual_idx", 0)
        session_data.setdefault("etapas", [])
        session_data.setdefault("decisoes", [])
        session_data.setdefault("fluxograma_gerado", False)
        session_data.setdefault("nome_processo", "Processo")
        return session_data

    def _importar_dados_pdf(self, ctx: Dict[str, Any]):
        if self.dados_pdf.get("atividade") or self.dados_pdf.get("titulo"):
            ctx["nome_processo"] = (
                self.dados_pdf.get("atividade") or self.dados_pdf.get("titulo")
            )
        if self.dados_pdf.get("sistemas"):
            ctx["sistemas_pdf"] = self.dados_pdf["sistemas"]

    def _extrair_lista(self, texto: str) -> List[str]:
        texto_limpo = re.sub(r"^\d+[\.)]\s*", "", texto, flags=re.MULTILINE)
        itens = re.split(r"[,;\n]+", texto_limpo)
        itens_limpos = [item.strip() for item in itens if item.strip()]
        return itens_limpos if itens_limpos else [texto.strip()]

    def _calc_percentual(self, ctx: Dict[str, Any]) -> int:
        idx = ctx.get("campo_atual_idx", 0)
        total = len(self.CAMPOS_FLUXOGRAMA)
        if idx == 0:
            return 5
        return min(int((idx / total) * 95) + 5, 100)

    @staticmethod
    def _sanitize(text: str) -> str:
        """Remove caracteres que quebram sintaxe Mermaid."""
        return text.replace('"', "'").replace("[", "(").replace("]", ")")


# Alias
HelenaFlowchartAgent = FlowchartAgent
