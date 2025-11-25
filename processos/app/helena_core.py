"""
Helena Core - Orquestrador Central dos Produtos Helena

Responsável por:
- Roteamento entre produtos (etapas, pop, fluxograma, etc.)
- Orquestração stateless
- Detecção inteligente de mudança de contexto
"""
import logging
import uuid
from typing import Dict, Any, Optional
from processos.domain.base import BaseHelena
from processos.models_new.chat_session import ChatSession
from processos.infra.session_manager import SessionManager

logger = logging.getLogger(__name__)


class HelenaCore:
    """
    Orquestrador central stateless para produtos Helena.

    Características:
    - Stateless: todo estado vem do SessionManager
    - Registry: produtos registrados dinamicamente
    - Roteamento: detecta mudanças de contexto automaticamente
    - Extensível: adicionar novos produtos sem modificar código

    Uso:
        core = HelenaCore(registry={
            'etapas': HelenaEtapas(),
            'pop': HelenaPOP(),
        })
        resultado = core.processar_mensagem(
            mensagem="Olá Helena",
            session_id="123-456",
            user=request.user
        )
    """

    def __init__(self, registry: Dict[str, BaseHelena]):
        """
        Inicializa orquestrador.

        Args:
            registry: Dicionário de CLASSES (não instâncias) de produtos Helena
                      {'etapas': HelenaEtapas, 'pop': HelenaPOP, ...}

        Raises:
            ValueError: Se registry vazio ou produtos inválidos
        """
        if not registry:
            raise ValueError("Registry não pode ser vazio")

        self.registry = registry
        self.session_manager = SessionManager()

        logger.info(f"HelenaCore inicializado com {len(registry)} produtos: {list(registry.keys())}")

    def processar_mensagem(
        self,
        mensagem: str,
        session_id: str,
        user,
        req_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa mensagem do usuário.

        Fluxo:
        1. Busca/cria sessão (SessionManager)
        2. Detecta mudança de contexto (se necessário)
        3. Delega para produto Helena específico
        4. Salva mensagens (user + assistant)
        5. Atualiza estado e cache
        6. Retorna resposta

        Args:
            mensagem: Texto do usuário
            session_id: UUID da sessão (string)
            user: Usuário Django autenticado
            req_uuid: UUID do request (para idempotência)

        Returns:
            dict: {
                'resposta': str,
                'session_id': str,
                'contexto_atual': str,
                'agentes_disponiveis': list[str],
                'progresso': Optional[str],
                'sugerir_contexto': Optional[str],
                'metadados': dict,
                'tipo_interface': Optional[str],  # Ex: 'areas', 'dropdown_macro'
                'dados_interface': Optional[dict]  # Dados para renderizar interface
            }

        Raises:
            ValueError: Se mensagem inválida ou sessão com problemas
        """
        if not mensagem or not isinstance(mensagem, str):
            raise ValueError("Mensagem deve ser uma string não-vazia")

        if req_uuid is None:
            req_uuid = str(uuid.uuid4())

        logger.info(f"Processando mensagem: session={session_id}, user={user.username}")

        # 1. Busca ou cria sessão
        session = self.session_manager.get_or_create_session(
            session_id=session_id,
            user=user
        )

        # 2. Detecta mudança de contexto
        novo_contexto = self._detectar_mudanca_contexto(mensagem, session)
        if novo_contexto and novo_contexto != session.contexto_atual:
            logger.info(f"Mudança de contexto detectada: {session.contexto_atual} → {novo_contexto}")
            session.contexto_atual = novo_contexto
            session.save(update_fields=['contexto_atual', 'atualizado_em'])

        # 3. Pega produto Helena ativo
        produto = self.registry.get(session.contexto_atual)
        if not produto:
            logger.error(f"Contexto inválido: {session.contexto_atual}")
            return self._resposta_erro(
                f"Contexto '{session.contexto_atual}' não encontrado. "
                f"Disponíveis: {', '.join(self.registry.keys())}",
                session
            )

        # 4. Carrega estado do produto (ou inicializa)
        if session.contexto_atual not in session.estados:
            # Estado novo - verificar se produto suporta skip_intro
            # Para HelenaPOP: frontend já mostra mensagem de boas-vindas hardcoded
            skip_intro = session.contexto_atual == 'pop'
            try:
                estado_produto = produto.inicializar_estado(skip_intro=skip_intro)
            except TypeError:
                # Produto não suporta skip_intro (ex: HelenaEtapas)
                estado_produto = produto.inicializar_estado()
        else:
            estado_produto = session.estados[session.contexto_atual]

        # 5. Processa mensagem
        try:
            resultado = produto.processar(mensagem, estado_produto)
        except Exception as e:
            logger.exception(f"Erro ao processar mensagem em {session.contexto_atual}: {e}")
            return self._resposta_erro(
                f"Desculpe, ocorreu um erro ao processar sua mensagem. "
                f"Por favor, tente novamente.",
                session
            )

        # 6. Atualiza estado do produto
        session.estados[session.contexto_atual] = resultado['novo_estado']

        # 7. Atualiza versão do agente
        session.agent_versions[session.contexto_atual] = produto.get_version()

        # 8. Salva no banco
        session.save(update_fields=['estados', 'agent_versions', 'atualizado_em'])

        # 9. Salva mensagens (idempotência via req_uuid)
        self.session_manager.save_message(
            session=session,
            role='user',
            content=mensagem,
            req_uuid=req_uuid,
            contexto=session.contexto_atual
        )

        resp_uuid = str(uuid.uuid4())

        # ✅ BUGFIX: Incluir tipo_interface e dados_interface em metadados
        # para que possam ser recuperados ao carregar histórico
        metadados_completos = resultado.get('metadados', {}).copy()
        if resultado.get('tipo_interface'):
            metadados_completos['tipo_interface'] = resultado['tipo_interface']
        if resultado.get('dados_interface'):
            metadados_completos['dados_interface'] = resultado['dados_interface']

        self.session_manager.save_message(
            session=session,
            role='assistant',
            content=resultado['resposta'],
            req_uuid=resp_uuid,
            contexto=session.contexto_atual,
            metadados=metadados_completos
        )

        # 10. Incrementa contador e verifica sync
        self.session_manager.cache.increment_message_count(session_id)

        # 11. Verificar se produto solicitou mudança de contexto
        metadados = resultado.get('metadados', {})
        if 'mudar_contexto' in metadados:
            novo_contexto = metadados['mudar_contexto']
            logger.info(f"[HELENA CORE] Produto {session.contexto_atual} solicitou mudança para {novo_contexto}")

            # Mudar contexto da sessão
            session.contexto_atual = novo_contexto

            # Inicializar estado do novo produto se não existir
            if novo_contexto not in session.estados:
                novo_produto = self.registry.get(novo_contexto)
                if novo_produto:
                    try:
                        # Tentar inicializar com dados herdados
                        dados_herdados = metadados.get('dados_herdados', {})
                        session.estados[novo_contexto] = novo_produto.inicializar_estado(dados_herdados=dados_herdados)
                    except TypeError:
                        # Se não suportar dados_herdados, inicializar normal
                        session.estados[novo_contexto] = novo_produto.inicializar_estado()

                    session.agent_versions[novo_contexto] = novo_produto.get_version()

            # Salvar mudanças
            session.save(update_fields=['contexto_atual', 'estados', 'agent_versions', 'atualizado_em'])
            logger.info(f"[HELENA CORE] Contexto mudado para {novo_contexto}")

            # 🎯 NOVO: Processar mensagem de inicialização automática no novo produto
            # Isso permite que o novo produto envie sua primeira pergunta automaticamente
            novo_produto = self.registry.get(novo_contexto)
            if novo_produto:
                logger.info(f"[HELENA CORE] Processando inicialização automática em {novo_contexto}")

                # Processar com mensagem de inicialização
                resultado_init = novo_produto.processar("iniciar", session.estados[novo_contexto])

                # Atualizar estado do novo produto
                session.estados[novo_contexto] = resultado_init.get('novo_estado', session.estados[novo_contexto])
                session.save(update_fields=['estados', 'atualizado_em'])

                # ✨ MODIFICAR a resposta para incluir AMBAS as mensagens
                # Concatenar a mensagem de despedida do produto antigo + primeira pergunta do novo
                resposta_init = resultado_init.get('resposta', '')
                resultado['resposta'] = resultado['resposta'] + "\n\n---\n\n" + resposta_init

                # Adicionar interface do novo produto, se houver
                if 'tipo_interface' in resultado_init:
                    resultado['tipo_interface'] = resultado_init['tipo_interface']
                if 'dados_interface' in resultado_init:
                    resultado['dados_interface'] = resultado_init['dados_interface']

                metadados['contexto_mudou'] = True
                logger.info(f"[HELENA CORE] Primeira pergunta do {novo_contexto} concatenada à resposta")

        # 12. Monta resposta
        response = {
            'resposta': resultado['resposta'],
            'session_id': session_id,
            'contexto_atual': session.contexto_atual,  # Pode ter mudado
            'agentes_disponiveis': list(self.registry.keys()),
            'progresso': resultado.get('progresso'),
            'sugerir_contexto': resultado.get('sugerir_contexto'),
            'metadados': {
                'agent_version': produto.get_version(),
                'agent_name': produto.get_nome(),
                **resultado.get('metadados', {})
            }
        }

        # 13. Adiciona interface dinâmica se houver
        if 'tipo_interface' in resultado:
            response['tipo_interface'] = resultado['tipo_interface']

        if 'dados_interface' in resultado:
            response['dados_interface'] = resultado['dados_interface']

        # ✅ FIX CRÍTICO: Passar dados_extraidos e formulario_pop do produto para frontend
        if 'dados_extraidos' in resultado:
            response['dados_extraidos'] = resultado['dados_extraidos']

        if 'formulario_pop' in resultado:
            response['formulario_pop'] = resultado['formulario_pop']

        return response

    def mudar_contexto(
        self,
        session_id: str,
        novo_contexto: str,
        user
    ) -> Dict[str, Any]:
        """
        Muda contexto explicitamente (sem processar mensagem).

        Args:
            session_id: UUID da sessão
            novo_contexto: Nome do novo produto
            user: Usuário autenticado

        Returns:
            dict: Confirmação da mudança

        Raises:
            ValueError: Se contexto inválido
        """
        if novo_contexto not in self.registry:
            raise ValueError(
                f"Contexto '{novo_contexto}' inválido. "
                f"Disponíveis: {', '.join(self.registry.keys())}"
            )

        session = self.session_manager.get_or_create_session(session_id, user)
        contexto_anterior = session.contexto_atual

        session.contexto_atual = novo_contexto
        session.save(update_fields=['contexto_atual', 'atualizado_em'])

        produto = self.registry[novo_contexto]

        logger.info(f"Contexto mudado manualmente: {contexto_anterior} → {novo_contexto}")

        return {
            'resposta': f"Contexto alterado para **{produto.get_nome()}**. Como posso ajudar?",
            'session_id': session_id,
            'contexto_atual': novo_contexto,
            'contexto_anterior': contexto_anterior,
            'agentes_disponiveis': list(self.registry.keys()),
        }

    def _detectar_mudanca_contexto(
        self,
        mensagem: str,
        session: ChatSession
    ) -> Optional[str]:
        """
        Detecta se usuário quer mudar de contexto.

        Estratégia:
        1. Pergunta ao produto atual primeiro (ele pode sugerir)
        2. Se não sugeriu, usa detecção por palavras-chave

        Args:
            mensagem: Texto do usuário
            session: Sessão atual

        Returns:
            str: Nome do novo contexto ou None
        """
        produto_atual = self.registry.get(session.contexto_atual)
        if produto_atual:
            # Produto atual pode sugerir mudança
            sugestao = produto_atual.detectar_intencao_mudanca_contexto(mensagem)
            if sugestao and sugestao in self.registry:
                return sugestao

        # Fallback: detecção básica por keywords
        msg_lower = mensagem.lower()

        # Comandos explícitos
        if 'mudar para' in msg_lower or 'trocar para' in msg_lower:
            for contexto in self.registry.keys():
                if contexto in msg_lower:
                    return contexto

        return None

    def _resposta_erro(
        self,
        mensagem_erro: str,
        session: ChatSession
    ) -> Dict[str, Any]:
        """
        Cria resposta de erro padronizada.

        Args:
            mensagem_erro: Mensagem de erro
            session: Sessão atual

        Returns:
            dict: Resposta de erro
        """
        return {
            'resposta': mensagem_erro,
            'session_id': str(session.session_id),
            'contexto_atual': session.contexto_atual,
            'agentes_disponiveis': list(self.registry.keys()),
            'erro': True,
        }

    def listar_produtos(self) -> Dict[str, Dict[str, str]]:
        """
        Lista todos os produtos Helena disponíveis.

        Returns:
            dict: {
                'etapas': {'nome': 'Helena Etapas', 'versao': '1.0.0'},
                ...
            }
        """
        return {
            nome: {
                'nome': produto.get_nome(),
                'versao': produto.get_version(),
            }
            for nome, produto in self.registry.items()
        }

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Retorna informações da sessão.

        Args:
            session_id: UUID da sessão

        Returns:
            dict: Estatísticas e estado da sessão
        """
        return self.session_manager.get_session_stats(session_id)

    def finalizar_sessao(self, session_id: str) -> None:
        """
        Finaliza sessão (ao fechar chat).

        Args:
            session_id: UUID da sessão
        """
        self.session_manager.finalize_session(session_id)
        logger.info(f"Sessão finalizada via HelenaCore: {session_id}")

    def processar_puro(
        self,
        contexto: str,
        mensagem: str,
        estado_atual: dict
    ) -> Dict[str, Any]:
        """
        Processa mensagem de forma PURA (sem Django, sem Redis, sem DB).

        Este método é stateless e não depende de infraestrutura externa.
        A view é responsável por carregar/salvar o estado.

        Args:
            contexto: Nome do produto ativo ('pop', 'etapas', etc.)
            mensagem: Texto do usuário
            estado_atual: Estado atual do produto (dict)

        Returns:
            dict: {
                'resposta': str,            # Resposta para o usuário
                'novo_estado': dict,        # Estado atualizado
                'contexto': str,            # Contexto após processamento (pode mudar!)
                'tipo_interface': str|None, # Interface dinâmica
                'dados_interface': dict|None, # Dados da interface
                'metadados': dict           # Metadados extras
            }

        Exemplo:
            >>> core = get_helena_core()
            >>> resultado = core.processar_puro(
            ...     contexto='pop',
            ...     mensagem='Carla',
            ...     estado_atual={}
            ... )
            >>> print(resultado['contexto'])  # 'pop'
            >>> print(resultado['resposta'])  # Resposta da Helena
        """
        # 1. Validar contexto
        if contexto not in self.registry:
            raise ValueError(
                f"Contexto '{contexto}' inválido. "
                f"Disponíveis: {', '.join(self.registry.keys())}"
            )

        # 2. Instanciar produto (classe, não instância)
        produto_cls = self.registry[contexto]
        produto = produto_cls()

        # 3. Processar mensagem
        resultado = produto.processar(mensagem, estado_atual)

        # 4. Verificar se há transição de contexto
        metadados = resultado.get('metadados', {})
        mudar_para = metadados.get('mudar_contexto')

        if not mudar_para:
            # Sem transição: continua no mesmo produto
            return {
                'resposta': resultado['resposta'],
                'novo_estado': resultado['novo_estado'],
                'contexto': contexto,
                'tipo_interface': resultado.get('tipo_interface'),
                'dados_interface': resultado.get('dados_interface'),
                'dados_extraidos': resultado.get('dados_extraidos'),  # ← Para formulário POP
                'metadados': metadados,
            }

        # 5. Há transição (ex: POP → Etapas)
        novo_contexto = mudar_para
        dados_herdados = metadados.get('dados_herdados', {})

        logger.info(f"[CORE PURO] Transição detectada: {contexto} → {novo_contexto}")

        # 6. Inicializar novo produto
        novo_produto_cls = self.registry[novo_contexto]
        novo_produto = novo_produto_cls()

        # 7. Inicializar estado do novo produto com dados herdados
        try:
            estado_inicial = novo_produto.inicializar_estado(dados_herdados=dados_herdados)
        except TypeError:
            # Produto não aceita dados_herdados
            estado_inicial = novo_produto.inicializar_estado()

        # 8. Processar mensagem de inicialização
        resultado_novo = novo_produto.processar('iniciar', estado_inicial)

        # 9. Concatenar respostas
        resposta_total = resultado['resposta'] + "\n\n" + resultado_novo['resposta']

        logger.info(f"[CORE PURO] Transição concluída: {contexto} → {novo_contexto}")

        # 10. Retornar resultado da transição
        return {
            'resposta': resposta_total,
            'novo_estado': resultado_novo['novo_estado'],
            'contexto': novo_contexto,  # ← Mudou!
            'tipo_interface': resultado_novo.get('tipo_interface'),
            'dados_interface': resultado_novo.get('dados_interface'),
            'dados_extraidos': resultado_novo.get('dados_extraidos'),  # ← Para formulário
            'metadados': resultado_novo.get('metadados', {}),
        }
