"""
Helpers de UI - funções reutilizáveis para criar respostas padronizadas
"""
from typing import Dict, Any, Optional
from processos.domain.helena_mapeamento.domain_old.enums import TipoInterface


def criar_resposta_padrao(
    resposta: str,
    tipo_interface: TipoInterface,
    dados_interface: Optional[Dict[str, Any]] = None,
    dados_extraidos: Optional[Dict[str, Any]] = None,
    conversa_completa: bool = False,
    progresso: str = "0/10",
    proximo_estado: str = "nome"
) -> Dict[str, Any]:
    """
    Cria resposta padronizada para o frontend (DRY)

    Args:
        resposta: Texto da resposta para o usuário
        tipo_interface: Tipo de interface (Enum)
        dados_interface: Dados específicos da interface (opções, etc)
        dados_extraidos: Dados extraídos da conversa
        conversa_completa: Se conversa foi finalizada
        progresso: String de progresso (ex: "5/10")
        proximo_estado: Próximo estado esperado

    Returns:
        Dicionário no formato esperado pelo frontend
    """
    return {
        "resposta": resposta,
        "tipo_interface": tipo_interface.value,
        "dados_interface": dados_interface or {},
        "dados_extraidos": dados_extraidos or {},
        "conversa_completa": conversa_completa,
        "progresso": progresso,
        "proximo_estado": proximo_estado
    }


def handle_edition_complete(
    campo: str,
    valor: Any,
    gerar_dados_completos_fn,
    gerar_codigo_fn
) -> Dict[str, Any]:
    """
    Centraliza lógica de "edição concluída, voltar para revisão"

    Substitui 10 blocos idênticos espalhados pelos métodos de processamento

    Args:
        campo: Nome do campo editado (ex: "area", "sistemas")
        valor: Novo valor do campo
        gerar_dados_completos_fn: Função self._gerar_dados_completos_pop
        gerar_codigo_fn: Função self._gerar_codigo_processo

    Returns:
        Dicionário de resposta para revisão
    """
    return {
        "resposta": f"Campo '{campo}' atualizado! Aqui está o resumo:",
        "tipo_interface": TipoInterface.REVISAO.value,
        "dados_interface": {
            "dados_completos": gerar_dados_completos_fn(),
            "codigo_gerado": gerar_codigo_fn()
        },
        "dados_extraidos": {campo: valor},
        "conversa_completa": False,
        "progresso": "10/10",
        "proximo_estado": "revisao"
    }
