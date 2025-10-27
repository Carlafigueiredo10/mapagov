"""
Base Helena - Contrato Abstrato para Produtos Conversacionais

Define o contrato que todos os produtos Helena devem seguir.
Garante consistência na interface e facilita extensibilidade.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)


class BaseHelena(ABC):
    """
    Classe abstrata base para todos os produtos Helena.

    Responsabilidades:
    - Define interface padrão (processar, inicializar_estado)
    - Gerencia versionamento do agente
    - Fornece métodos auxiliares comuns

    Todas as Helenas devem:
    1. Ser stateless (sem self.estado)
    2. Receber estado via parâmetro
    3. Retornar novo estado no resultado
    """

    VERSION = "1.0.0"  # Versionamento semântico (MAJOR.MINOR.PATCH)
    PRODUTO_NOME = "Helena Base"  # Sobrescrever nas subclasses

    def __init__(self):
        """Inicialização básica - não deve conter estado mutável"""
        logger.info(f"Inicializando {self.PRODUTO_NOME} v{self.VERSION}")

    @abstractmethod
    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa uma mensagem do usuário.

        Args:
            mensagem: Texto enviado pelo usuário
            session_data: Estado atual da sessão (JSON do DB/Redis)
                Estrutura esperada: {
                    'etapa_atual': int,
                    'dados_coletados': dict,
                    'historico': list,
                    ...
                }

        Returns:
            dict com estrutura:
            {
                'resposta': str,  # Resposta para o usuário
                'novo_estado': dict,  # Estado atualizado (será salvo)
                'progresso': Optional[str],  # Ex: "2/5 etapas"
                'sugerir_contexto': Optional[str],  # Ex: 'fluxograma'
                'metadados': Optional[dict]  # Dados extras (tokens usados, etc)
            }

        Raises:
            ValueError: Se mensagem vazia ou session_data inválido
        """
        pass

    @abstractmethod
    def inicializar_estado(self) -> dict:
        """
        Retorna estado inicial limpo para este produto.

        Returns:
            dict: Estado inicial (será usado na primeira interação)

        Exemplo:
            {'etapa_atual': 0, 'dados_coletados': {}, 'historico': []}
        """
        pass

    def get_version(self) -> str:
        """Retorna versão do agente"""
        return self.VERSION

    def get_nome(self) -> str:
        """Retorna nome do produto"""
        return self.PRODUTO_NOME

    def validar_mensagem(self, mensagem: str) -> None:
        """
        Valida mensagem de entrada.

        Args:
            mensagem: Texto a validar

        Raises:
            ValueError: Se mensagem inválida
        """
        if not mensagem or not isinstance(mensagem, str):
            raise ValueError("Mensagem deve ser uma string não-vazia")

        if len(mensagem.strip()) == 0:
            raise ValueError("Mensagem não pode ser apenas espaços")

        if len(mensagem) > 10000:  # Limite de segurança
            raise ValueError("Mensagem muito longa (máx 10.000 caracteres)")

    def validar_session_data(self, session_data: dict) -> None:
        """
        Valida estrutura de session_data.

        Args:
            session_data: Estado da sessão

        Raises:
            ValueError: Se session_data inválido
        """
        if not isinstance(session_data, dict):
            raise ValueError("session_data deve ser um dicionário")

    def criar_resposta(
        self,
        resposta: str,
        novo_estado: dict,
        progresso: Optional[str] = None,
        sugerir_contexto: Optional[str] = None,
        metadados: Optional[dict] = None,
        tipo_interface: Optional[str] = None,
        dados_interface: Optional[dict] = None,
        formulario_pop: Optional[dict] = None,  # ✅ FASE 2: Novo nome
        dados_extraidos: Optional[dict] = None  # ✅ FIX: Compatibilidade com frontend OLD
    ) -> dict:
        """
        Helper para criar resposta padronizada.

        Args:
            resposta: Texto de resposta
            novo_estado: Estado atualizado
            progresso: String de progresso (ex: "3/5")
            sugerir_contexto: Contexto sugerido para mudança
            metadados: Dados extras
            tipo_interface: Tipo de interface dinâmica (ex: 'areas', 'dropdown_macro')
            dados_interface: Dados para renderizar a interface
            formulario_pop: Dados do formulário POP (FASE 2 - novo nome)
            dados_extraidos: Dados extraídos (compatibilidade com frontend OLD)

        Returns:
            dict: Resposta formatada
        """
        resultado = {
            'resposta': resposta,
            'novo_estado': novo_estado,
        }

        if progresso:
            resultado['progresso'] = progresso

        if sugerir_contexto:
            resultado['sugerir_contexto'] = sugerir_contexto

        if metadados:
            resultado['metadados'] = metadados

        if tipo_interface:
            resultado['tipo_interface'] = tipo_interface

        if dados_interface:
            resultado['dados_interface'] = dados_interface

        if formulario_pop:
            resultado['formulario_pop'] = formulario_pop

        if dados_extraidos:
            resultado['dados_extraidos'] = dados_extraidos

        return resultado

    def detectar_intencao_mudanca_contexto(self, mensagem: str) -> Optional[str]:
        """
        Detecta se usuário quer mudar de contexto.

        Args:
            mensagem: Texto do usuário

        Returns:
            str: Nome do contexto sugerido ou None

        Exemplo:
            "quero fazer um fluxograma" -> "fluxograma"
            "como mapear riscos?" -> "riscos"
        """
        msg_lower = mensagem.lower()

        # Mapeamento de palavras-chave para contextos
        contextos = {
            'fluxograma': ['fluxograma', 'diagrama', 'flowchart'],
            'riscos': ['risco', 'riscos', 'análise de risco'],
            'pop': ['pop', 'procedimento', 'operacional padrão'],
            'mapeamento': ['mapear', 'mapeamento', 'processo'],
            'conformidade': ['conformidade', 'compliance', 'regulamento'],
        }

        for contexto, palavras_chave in contextos.items():
            if any(palavra in msg_lower for palavra in palavras_chave):
                return contexto

        return None

    def log_event(
        self,
        evento: str,
        dados: Optional[Dict[str, Any]] = None,
        nivel: str = "info"
    ) -> None:
        """
        Registra evento estruturado com contexto.

        Args:
            evento: Nome do evento (ex: "estado_mudou", "erro_validacao")
            dados: Dados adicionais do evento
            nivel: Nível de log ("debug", "info", "warning", "error", "critical")

        Exemplo:
            self.log_event("estado_mudou", {
                "de": "nome_usuario",
                "para": "area_decipex",
                "timestamp": time.time()
            })
        """
        # Criar contexto estruturado
        contexto = {
            "produto": self.PRODUTO_NOME,
            "versao": self.VERSION,
            "evento": evento,
            "timestamp": time.time(),
        }

        if dados:
            contexto.update(dados)

        # Log estruturado
        log_msg = f"[{self.PRODUTO_NOME}] {evento}"

        if nivel == "debug":
            logger.debug(log_msg, extra=contexto)
        elif nivel == "info":
            logger.info(log_msg, extra=contexto)
        elif nivel == "warning":
            logger.warning(log_msg, extra=contexto)
        elif nivel == "error":
            logger.error(log_msg, extra=contexto)
        elif nivel == "critical":
            logger.critical(log_msg, extra=contexto)
        else:
            logger.info(log_msg, extra=contexto)

    def chamar_modelo(
        self,
        prompt: str,
        provider: str = "vertex",
        model: Optional[str] = None,
        temperatura: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Hook genérico para chamar modelos de IA (Vertex AI, OpenAI, etc).

        Args:
            prompt: Prompt a ser enviado ao modelo
            provider: Provider do modelo ("vertex", "openai", "anthropic")
            model: Nome específico do modelo (opcional, usa padrão do provider)
            temperatura: Temperatura de geração (0.0-1.0)
            max_tokens: Número máximo de tokens

        Returns:
            dict: {
                'texto': str,  # Resposta do modelo
                'tokens_usados': int,
                'modelo': str,
                'provider': str
            }

        Raises:
            NotImplementedError: Se provider não implementado
            Exception: Se erro ao chamar API

        Exemplo:
            resposta = self.chamar_modelo(
                prompt="Sugira 3 normas para este processo",
                provider="vertex",
                temperatura=0.3
            )
            print(resposta['texto'])
        """
        # Log evento
        self.log_event("chamar_modelo", {
            "provider": provider,
            "model": model,
            "temperatura": temperatura
        }, nivel="debug")

        # Implementações por provider
        if provider == "vertex":
            return self._chamar_vertex(prompt, model, temperatura, max_tokens)
        elif provider == "openai":
            return self._chamar_openai(prompt, model, temperatura, max_tokens)
        elif provider == "anthropic":
            return self._chamar_anthropic(prompt, model, temperatura, max_tokens)
        else:
            raise NotImplementedError(f"Provider '{provider}' não implementado")

    def _chamar_vertex(
        self,
        prompt: str,
        model: Optional[str],
        temperatura: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Implementação para Vertex AI"""
        try:
            from google.cloud import aiplatform
            from vertexai.preview.generative_models import GenerativeModel

            if model is None:
                model = "gemini-pro"

            gen_model = GenerativeModel(model)
            response = gen_model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperatura,
                    "max_output_tokens": max_tokens
                }
            )

            return {
                'texto': response.text,
                'tokens_usados': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                'modelo': model,
                'provider': 'vertex'
            }

        except ImportError:
            logger.warning("google-cloud-aiplatform não instalado")
            raise NotImplementedError("Vertex AI não disponível (biblioteca não instalada)")
        except Exception as e:
            logger.error(f"Erro ao chamar Vertex AI: {e}")
            raise

    def _chamar_openai(
        self,
        prompt: str,
        model: Optional[str],
        temperatura: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Implementação para OpenAI"""
        try:
            import openai

            if model is None:
                model = "gpt-3.5-turbo"

            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperatura,
                max_tokens=max_tokens
            )

            return {
                'texto': response.choices[0].message.content,
                'tokens_usados': response.usage.total_tokens,
                'modelo': model,
                'provider': 'openai'
            }

        except ImportError:
            logger.warning("openai não instalado")
            raise NotImplementedError("OpenAI não disponível (biblioteca não instalada)")
        except Exception as e:
            logger.error(f"Erro ao chamar OpenAI: {e}")
            raise

    def _chamar_anthropic(
        self,
        prompt: str,
        model: Optional[str],
        temperatura: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Implementação para Anthropic Claude"""
        try:
            import anthropic

            if model is None:
                model = "claude-3-sonnet-20240229"

            client = anthropic.Anthropic()
            response = client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperatura,
                max_tokens=max_tokens
            )

            return {
                'texto': response.content[0].text,
                'tokens_usados': response.usage.input_tokens + response.usage.output_tokens,
                'modelo': model,
                'provider': 'anthropic'
            }

        except ImportError:
            logger.warning("anthropic não instalado")
            raise NotImplementedError("Anthropic não disponível (biblioteca não instalada)")
        except Exception as e:
            logger.error(f"Erro ao chamar Anthropic: {e}")
            raise

    def __str__(self) -> str:
        return f"{self.PRODUTO_NOME} v{self.VERSION}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(version='{self.VERSION}')>"
