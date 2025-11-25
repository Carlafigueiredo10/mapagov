"""
Protocol para Produtos Helena - Contrato explícito

Define o contrato que TODOS os produtos Helena devem seguir.
Usar este Protocol garante que novos produtos sejam compatíveis com HelenaCore.

Exemplos de produtos:
- HelenaPOP
- HelenaEtapas
- HelenaOKR (futuro)
- HelenaPlanejamento (futuro)
"""
from typing import Protocol, Dict, Any, Optional


class ProdutoHelenaProtocol(Protocol):
    """
    Contrato que todo produto Helena deve implementar.

    Um produto Helena é responsável por:
    1. Processar mensagens do usuário
    2. Gerenciar seu próprio estado
    3. Sinalizar mudanças de contexto via metadados

    Exemplo de implementação:
        class MinhaHelena(BaseHelena):
            def processar(self, mensagem: str, estado: dict) -> dict:
                # Lógica de processamento
                return {
                    'resposta': "Texto para o usuário",
                    'novo_estado': {'campo': 'valor'},
                    'metadados': {}
                }

            def inicializar_estado(self, dados_herdados=None) -> dict:
                return {}
    """

    def processar(self, mensagem: str, estado: dict) -> dict:
        """
        Processa uma mensagem do usuário.

        Args:
            mensagem: Texto enviado pelo usuário
            estado: Estado atual deste produto (dict serializável)

        Returns:
            dict com estrutura OBRIGATÓRIA:
            {
                'resposta': str,         # Texto para o usuário (obrigatório)
                'novo_estado': dict,     # Estado atualizado (obrigatório)
                'tipo_interface': str|None,   # Ex: 'areas', 'dropdown' (opcional)
                'dados_interface': dict|None, # Dados da interface (opcional)
                'metadados': dict        # Metadados extras (opcional)
            }

        Estrutura de metadados (OPCIONAL):
            {
                # Para solicitar mudança de contexto:
                'mudar_contexto': 'etapas' | 'pop' | 'outro',

                # Dados a passar para o próximo produto:
                'dados_herdados': {
                    'area': {...},
                    'sistemas': [...],
                    # ...
                },

                # Outros metadados personalizados:
                'progresso_detalhado': {...},
                'badge': {...},
                # ...
            }

        Exemplo de transição:
            # Quando HelenaPOP quer ir para HelenaEtapas:
            return {
                'resposta': "Passando para Helena Etapas...",
                'novo_estado': sm.to_dict(),
                'metadados': {
                    'mudar_contexto': 'etapas',
                    'dados_herdados': {
                        'area': self.area_selecionada,
                        'sistemas': self.sistemas_coletados,
                    }
                }
            }

        Raises:
            ValueError: Se mensagem inválida
        """
        ...

    def inicializar_estado(
        self,
        dados_herdados: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Retorna estado inicial limpo para este produto.

        Args:
            dados_herdados: Dados recebidos do produto anterior (opcional)
                           Usado quando há transição de contexto

        Returns:
            dict: Estado inicial serializável

        Exemplo:
            def inicializar_estado(self, dados_herdados=None):
                estado = {
                    'etapa_atual': 0,
                    'dados_coletados': {}
                }

                # Se recebeu dados de outro produto:
                if dados_herdados:
                    estado['dados_herdados'] = dados_herdados

                return estado

        Nota:
            Este método PODE aceitar dados_herdados, mas não é obrigatório.
            Se o produto não usa dados herdados, pode ignorar o parâmetro.
        """
        ...


# Validação em tempo de desenvolvimento
def validar_produto(produto: Any) -> tuple[bool, str]:
    """
    Valida se um produto implementa o contrato correto.

    Args:
        produto: Instância ou classe do produto

    Returns:
        tuple: (valido: bool, mensagem_erro: str)

    Exemplo:
        >>> from processos.domain.helena_pop import HelenaPOP
        >>> valido, msg = validar_produto(HelenaPOP())
        >>> print(valido)  # True
    """
    # Verificar métodos obrigatórios
    if not hasattr(produto, 'processar'):
        return False, "Produto não implementa método 'processar'"

    if not hasattr(produto, 'inicializar_estado'):
        return False, "Produto não implementa método 'inicializar_estado'"

    # Verificar assinatura de processar
    import inspect
    sig_processar = inspect.signature(produto.processar)
    params_processar = list(sig_processar.parameters.keys())

    if 'mensagem' not in params_processar or 'estado' not in params_processar:
        return False, "Método 'processar' deve ter parâmetros (mensagem, estado)"

    # Verificar assinatura de inicializar_estado
    sig_init = inspect.signature(produto.inicializar_estado)
    # Aceita com ou sem dados_herdados

    return True, "Produto válido"


# Exemplo de uso em testes
if __name__ == '__main__':
    from processos.domain.helena_mapeamento.helena_pop import HelenaPOP
    from processos.domain.helena_mapeamento.helena_etapas import HelenaEtapas

    # Validar produtos existentes
    for produto_cls in [HelenaPOP, HelenaEtapas]:
        produto = produto_cls()
        valido, msg = validar_produto(produto)
        print(f"{produto_cls.__name__}: {msg}")
