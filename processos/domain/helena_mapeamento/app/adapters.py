"""
Adaptadores de UI - traduzem sinais da StateMachine para formato esperado pelo frontend
"""
from typing import Dict, Any, List
from processos.domain.helena_mapeamento.domain_old.enums import TipoInterface


def adapter_etapas_ui(
    resultado_sm: Dict[str, Any],
    etapa_sm,  # EtapaStateMachine
    operadores_disponiveis: List[str],
    calcular_progresso_fn,
    criar_resposta_tempo_real_fn=None
) -> Dict[str, Any]:
    """
    Traduz sinais da EtapaStateMachine para resposta JSON esperada pelo frontend

    Args:
        resultado_sm: Resultado retornado por EtapaStateMachine.processar()
        etapa_sm: Instância da máquina de estados
        operadores_disponiveis: Lista de operadores (ex: OPERADORES_DECIPEX)
        calcular_progresso_fn: Função para calcular progresso (self._calcular_progresso)
        criar_resposta_tempo_real_fn: Função opcional para modo tempo real

    Returns:
        Dicionário no formato esperado pelo frontend:
        {
            "resposta": "...",
            "tipo_interface": "...",
            "dados_interface": {...},
            "dados_extraidos": {...},
            "conversa_completa": False,
            "progresso": "8/10",
            "proximo_estado": "etapas"
        }
    """

    # ✅ FIX: PRIORIZAR perguntas sobre transições de estado
    # Sinal: Perguntar sobre condicionais (DEVE VIR ANTES DE "OPERADOR")
    if resultado_sm.get("pergunta") == "tem_condicionais?":
        resposta_base = {
            "resposta": f"Operador definido: {resultado_sm['operador']}\n\nEssa etapa tem alguma decisão ou condição (sim/não)?",
            "tipo_interface": TipoInterface.CONDICIONAIS.value,
            "dados_interface": {
                "numero_etapa": etapa_sm.numero,
                "descricao_etapa": etapa_sm.descricao
            },
            "dados_extraidos": {"operador_etapa": resultado_sm['operador']},
            "conversa_completa": False,
            "progresso": calcular_progresso_fn(),
            "proximo_estado": "etapas"
        }
        return _aplicar_tempo_real(resposta_base, criar_resposta_tempo_real_fn)

    # Sinal: Perguntar tipo de condicional
    if resultado_sm.get("pergunta") == "tipo_condicional":
        resposta_base = {
            "resposta": f"Ótimo! A Etapa {etapa_sm.numero} tem condições/decisões.\n\nQuantos cenários possíveis existem nessa decisão?",
            "tipo_interface": TipoInterface.TIPO_CONDICIONAL.value,
            "dados_interface": {
                "numero_etapa": etapa_sm.numero,
                "opcoes": [
                    {"id": "binario", "label": "2 cenários (Sim/Não, Aprovado/Reprovado, Completo/Incompleto, etc)"},
                    {"id": "multiplos", "label": "Múltiplos cenários (3 ou mais opções diferentes)"}
                ]
            },
            "dados_extraidos": {"tem_condicionais": True},
            "conversa_completa": False,
            "progresso": calcular_progresso_fn(),
            "proximo_estado": "etapas"
        }
        return _aplicar_tempo_real(resposta_base, criar_resposta_tempo_real_fn)

    # Sinal: Perguntar o que fazer antes da decisão
    if resultado_sm.get("pergunta") == "antes_decisao":
        resposta_base = {
            "resposta": f"Certo! Vamos definir os cenários.\n\nAntes de tomar a decisão, o que deve ser feito?\n\nExemplo: 'Conferir documentação', 'Analisar valor do pedido', 'Verificar elegibilidade'\n\nO que deve ser feito ANTES da decisão?",
            "tipo_interface": TipoInterface.TEXTO.value,
            "dados_interface": {
                "numero_etapa": etapa_sm.numero,
                "tipo_condicional": resultado_sm['tipo'],
                "placeholder": "Ex: Conferir se a documentação está completa"
            },
            "dados_extraidos": {"tipo_condicional": resultado_sm['tipo']},
            "conversa_completa": False,
            "progresso": calcular_progresso_fn(),
            "proximo_estado": "etapas"
        }
        return _aplicar_tempo_real(resposta_base, criar_resposta_tempo_real_fn)

    # Sinal: Perguntar descrições dos cenários
    if resultado_sm.get("pergunta") == "cenarios_descricoes":
        # Pegar lista de etapas já criadas (para permitir referências)
        # NOTA: Isso precisa ser passado por quem chama o adapter
        etapas_criadas = []  # TODO: passar como parâmetro

        if etapa_sm.tipo_condicional == "binario":
            resposta_base = {
                "resposta": f"Perfeito! Antes da decisão: '{resultado_sm['antes_decisao']}'\n\n💡 *Lembre-se: na próxima fase vamos listar os documentos necessários, não esqueça!*\n\nAgora defina os 2 cenários:",
                "tipo_interface": TipoInterface.CENARIOS_BINARIO.value,
                "dados_interface": {
                    "numero_etapa": etapa_sm.numero,
                    "antes_decisao": resultado_sm['antes_decisao'],
                    "etapas_disponiveis": etapas_criadas
                },
                "dados_extraidos": {"antes_decisao": resultado_sm['antes_decisao']},
                "conversa_completa": False,
                "progresso": calcular_progresso_fn(),
                "proximo_estado": "etapas"
            }
        else:  # multiplos
            resposta_base = {
                "resposta": f"Perfeito! Antes da decisão: '{resultado_sm['antes_decisao']}'\n\n💡 *Lembre-se: na próxima fase vamos listar os documentos necessários, não esqueça!*\n\nQuantos cenários existem?",
                "tipo_interface": TipoInterface.CENARIOS_MULTIPLOS_QUANTIDADE.value,
                "dados_interface": {
                    "numero_etapa": etapa_sm.numero,
                    "antes_decisao": resultado_sm['antes_decisao'],
                    "etapas_disponiveis": etapas_criadas
                },
                "dados_extraidos": {"antes_decisao": resultado_sm['antes_decisao']},
                "conversa_completa": False,
                "progresso": calcular_progresso_fn(),
                "proximo_estado": "etapas"
            }
        return _aplicar_tempo_real(resposta_base, criar_resposta_tempo_real_fn)

    # Sinal: Perguntar subetapas de um cenário
    if resultado_sm.get("pergunta") == "subetapas":
        resposta_base = {
            "resposta": f"Cenários registrados! Agora vamos detalhar cada um.",
            "tipo_interface": TipoInterface.SUBETAPAS_CENARIO.value,
            "dados_interface": {
                "numero_cenario": resultado_sm['cenario_atual'],
                "descricao_cenario": resultado_sm['cenario_descricao'],
                "todos_cenarios": [c.to_dict() for c in etapa_sm.cenarios],
                "cenario_atual_index": etapa_sm._cenario_index
            },
            "dados_extraidos": {},
            "conversa_completa": False,
            "progresso": calcular_progresso_fn(),
            "proximo_estado": "etapas"
        }
        return _aplicar_tempo_real(resposta_base, criar_resposta_tempo_real_fn)

    # Sinal: Perguntar detalhes de etapa linear
    if resultado_sm.get("pergunta") == "detalhes":
        resposta_base = {
            "resposta": f"Entendido. Etapa {etapa_sm.numero} é linear (sem condições).\n\nAgora vamos aos detalhes/passos dessa etapa. Qual o primeiro detalhe?",
            "tipo_interface": TipoInterface.TEXTO.value,
            "dados_interface": {},
            "dados_extraidos": {"tem_condicionais": False},
            "conversa_completa": False,
            "progresso": calcular_progresso_fn(),
            "proximo_estado": "etapas"
        }
        return _aplicar_tempo_real(resposta_base, criar_resposta_tempo_real_fn)

    # Sinal: Perguntar mais detalhes
    if resultado_sm.get("pergunta") == "mais_detalhes":
        detalhe = resultado_sm['detalhe_adicionado']
        resposta_base = {
            "resposta": f"Detalhe registrado: {detalhe[:60]}{'...' if len(detalhe) > 60 else ''}\n\nHá mais algum detalhe dessa etapa? (Digite o próximo detalhe ou 'não' para finalizar detalhes)",
            "tipo_interface": TipoInterface.TEXTO.value,
            "dados_interface": {},
            "dados_extraidos": {"detalhe_adicionado": detalhe},
            "conversa_completa": False,
            "progresso": calcular_progresso_fn(),
            "proximo_estado": "etapas"
        }
        return _aplicar_tempo_real(resposta_base, criar_resposta_tempo_real_fn)

    # Sinal: Etapa finalizada (condicional ou linear)
    if "finalizada" in resultado_sm.get("status", ""):
        return {
            "resposta": f"Etapa {etapa_sm.numero} completa!\n\nHá mais alguma etapa? (Digite a próxima etapa ou 'não' para finalizar)",
            "tipo_interface": TipoInterface.TEXTO.value,
            "dados_interface": {},
            "dados_extraidos": {"etapa_adicionada": etapa_sm.obter_dict()},
            "conversa_completa": False,
            "progresso": calcular_progresso_fn(),
            "proximo_estado": "etapas"
        }

    # Sinal: Avançou para estado OPERADOR (MOVIDO PARA CÁ - MENOR PRIORIDADE)
    if resultado_sm.get("proximo") == "OPERADOR":
        resposta_base = {
            "resposta": f"Etapa {etapa_sm.numero} registrada: {resultado_sm['descricao']}\n\nQuem é o responsável por executar essa etapa?",
            "tipo_interface": TipoInterface.OPERADORES_ETAPA.value,
            "dados_interface": {
                "opcoes": operadores_disponiveis,
                "numero_etapa": etapa_sm.numero
            },
            "dados_extraidos": {},
            "conversa_completa": False,
            "progresso": calcular_progresso_fn(),
            "proximo_estado": "etapas"
        }
        return _aplicar_tempo_real(resposta_base, criar_resposta_tempo_real_fn)

    # Erro: sinal não reconhecido
    return {
        "resposta": "Desculpe, algo deu errado no processamento da etapa. Pode repetir?",
        "tipo_interface": TipoInterface.TEXTO.value,
        "dados_interface": {},
        "dados_extraidos": {},
        "conversa_completa": False,
        "progresso": calcular_progresso_fn(),
        "proximo_estado": "etapas"
    }


def _aplicar_tempo_real(resposta_base: Dict[str, Any], criar_tempo_real_fn) -> Dict[str, Any]:
    """Aplica modo tempo real se função fornecida"""
    if criar_tempo_real_fn:
        return criar_tempo_real_fn(resposta_base)
    return resposta_base
