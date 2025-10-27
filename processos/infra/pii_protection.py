"""
PII Protection - Proteção de Dados Pessoais Identificáveis

Responsável por:
- Detectar e mascarar CPF, CNPJ, e-mails, telefones
- Compliance LGPD antes de enviar dados para LLMs externos
- Reversibilidade (opcional): armazenar hash para reconstituir
"""
import re
import hashlib
import logging
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)


class PIIProtector:
    """
    Mascara dados pessoais sensíveis antes de enviar para LLMs.

    Uso:
        protector = PIIProtector()
        texto_seguro = protector.mask_all(texto_original)
    """

    # Padrões regex para detecção
    PATTERNS = {
        'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
        'cnpj': r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'telefone': r'\b(?:\+55\s?)?\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b',
        'cep': r'\b\d{5}-?\d{3}\b',
    }

    # Máscaras de substituição
    MASKS = {
        'cpf': '***.***.***-**',
        'cnpj': '**.***.***/****-**',
        'email': '***@***.***',
        'telefone': '(**) ****-****',
        'cep': '*****-***',
    }

    def __init__(self, enabled: bool = True):
        """
        Inicializa protetor.

        Args:
            enabled: Se False, desabilita proteção (dev/debug)
        """
        self.enabled = enabled
        self.detections: List[Dict] = []  # Log de detecções

        if not enabled:
            logger.warning("PIIProtector DESABILITADO - não use em produção!")

    def mask_all(self, text: str) -> str:
        """
        Mascara todos os tipos de PII.

        Args:
            text: Texto original

        Returns:
            str: Texto com PIIs mascarados
        """
        if not self.enabled or not text:
            return text

        masked_text = text
        self.detections = []

        for pii_type, pattern in self.PATTERNS.items():
            masked_text, count = self._mask_pattern(
                masked_text,
                pattern,
                self.MASKS[pii_type],
                pii_type
            )
            if count > 0:
                logger.info(f"Mascarados {count} {pii_type}(s)")
                self.detections.append({
                    'tipo': pii_type,
                    'quantidade': count
                })

        return masked_text

    def _mask_pattern(
        self,
        text: str,
        pattern: str,
        mask: str,
        pii_type: str
    ) -> Tuple[str, int]:
        """
        Mascara um padrão específico.

        Args:
            text: Texto original
            pattern: Regex para detecção
            mask: Máscara de substituição
            pii_type: Tipo de PII (para log)

        Returns:
            tuple: (texto_mascarado, quantidade_substituições)
        """
        matches = list(re.finditer(pattern, text))
        count = len(matches)

        if count == 0:
            return text, 0

        # Substitui do fim para o início (evita problemas de índice)
        for match in reversed(matches):
            start, end = match.span()
            original = text[start:end]

            # Log (apenas 3 primeiros chars para debug)
            preview = original[:3] + '...'
            logger.debug(f"PII detectado ({pii_type}): {preview}")

            text = text[:start] + mask + text[end:]

        return text, count

    def mask_cpf(self, text: str) -> str:
        """Mascara apenas CPFs"""
        if not self.enabled:
            return text
        masked, _ = self._mask_pattern(text, self.PATTERNS['cpf'], self.MASKS['cpf'], 'cpf')
        return masked

    def mask_email(self, text: str) -> str:
        """Mascara apenas e-mails"""
        if not self.enabled:
            return text
        masked, _ = self._mask_pattern(text, self.PATTERNS['email'], self.MASKS['email'], 'email')
        return masked

    def mask_telefone(self, text: str) -> str:
        """Mascara apenas telefones"""
        if not self.enabled:
            return text
        masked, _ = self._mask_pattern(text, self.PATTERNS['telefone'], self.MASKS['telefone'], 'telefone')
        return masked

    def detect_only(self, text: str) -> Dict[str, int]:
        """
        Apenas detecta PIIs sem mascarar (para análise).

        Args:
            text: Texto a analisar

        Returns:
            dict: {'cpf': 2, 'email': 1, ...}
        """
        if not text:
            return {}

        detections = {}
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detections[pii_type] = len(matches)

        return detections

    def has_pii(self, text: str) -> bool:
        """
        Verifica se texto contém algum PII.

        Args:
            text: Texto a verificar

        Returns:
            bool: True se contém PII
        """
        detections = self.detect_only(text)
        return len(detections) > 0

    def get_last_detections(self) -> List[Dict]:
        """
        Retorna log das últimas detecções (após mask_all).

        Returns:
            list: [{'tipo': 'cpf', 'quantidade': 2}, ...]
        """
        return self.detections


class PIIHashStore:
    """
    Armazena hash de PIIs para possível reconstituição (LGPD).

    Uso (opcional, para auditoria):
        store = PIIHashStore()
        hash_ref = store.hash_pii('123.456.789-00')
        # ... armazena hash_ref no banco
        # Se precisar recuperar (com justificativa legal):
        original = store.reverse_lookup(hash_ref)  # Requer DB
    """

    def __init__(self, salt: str = 'mapagov-pii-salt'):
        """
        Inicializa armazenador.

        Args:
            salt: Salt para hashing (deve vir de settings secreto)
        """
        self.salt = salt

    def hash_pii(self, pii_value: str) -> str:
        """
        Gera hash irreversível de um PII.

        Args:
            pii_value: Valor original (CPF, email, etc.)

        Returns:
            str: Hash SHA256
        """
        salted = f"{self.salt}:{pii_value}"
        return hashlib.sha256(salted.encode()).hexdigest()

    def verify_pii(self, pii_value: str, hash_ref: str) -> bool:
        """
        Verifica se um PII corresponde a um hash.

        Args:
            pii_value: Valor a verificar
            hash_ref: Hash armazenado

        Returns:
            bool: True se corresponde
        """
        return self.hash_pii(pii_value) == hash_ref


# Instância global (singleton)
_default_protector = None


def get_pii_protector() -> PIIProtector:
    """
    Retorna instância singleton do protector.

    Returns:
        PIIProtector: Instância compartilhada
    """
    global _default_protector
    if _default_protector is None:
        # Verifica se deve estar habilitado (settings)
        from django.conf import settings
        enabled = not getattr(settings, 'DEBUG', False)  # Desabilitado em DEBUG
        _default_protector = PIIProtector(enabled=enabled)
    return _default_protector


# Atalhos convenientes
def mask_pii(text: str) -> str:
    """Atalho para mascarar PIIs (usa instância global)"""
    return get_pii_protector().mask_all(text)


def detect_pii(text: str) -> Dict[str, int]:
    """Atalho para detectar PIIs (usa instância global)"""
    return get_pii_protector().detect_only(text)


def has_pii(text: str) -> bool:
    """Atalho para verificar se tem PII (usa instância global)"""
    return get_pii_protector().has_pii(text)
