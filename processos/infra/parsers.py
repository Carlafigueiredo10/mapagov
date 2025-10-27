"""
Parsers inteligentes com fuzzy matching para normalização de texto
"""
from typing import List
import re


def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos, espaços extras e convertendo para minúsculas"""
    # Remove espaços extras
    texto = ' '.join(texto.split())
    # Lowercase
    texto = texto.lower()
    # Remove pontuação comum
    texto = re.sub(r'[.,:;!?()-]', '', texto)
    return texto.strip()


def fuzzy_match(texto: str, opcoes: List[str], threshold: float = 0.7) -> str:
    """
    Encontra a melhor correspondência fuzzy

    Args:
        texto: Texto a ser comparado
        opcoes: Lista de opções válidas
        threshold: Limiar de similaridade (0-1)

    Returns:
        Melhor correspondência ou None
    """
    try:
        from difflib import SequenceMatcher

        texto_norm = normalizar_texto(texto)
        melhor_match = None
        melhor_score = 0

        for opcao in opcoes:
            opcao_norm = normalizar_texto(opcao)

            # Verificar match exato primeiro
            if texto_norm == opcao_norm:
                return opcao

            # Verificar se contém
            if texto_norm in opcao_norm or opcao_norm in texto_norm:
                return opcao

            # Calcular similaridade
            score = SequenceMatcher(None, texto_norm, opcao_norm).ratio()

            if score > melhor_score and score >= threshold:
                melhor_score = score
                melhor_match = opcao

        return melhor_match
    except:
        return None


def parse_sistemas(entrada: str, sistemas_validos: dict) -> List[str]:
    """
    Parse inteligente de sistemas com fuzzy matching

    Args:
        entrada: String com sistemas separados por vírgula
        sistemas_validos: Dict com categorias e sistemas válidos

    Returns:
        Lista de sistemas reconhecidos
    """
    # Flatten todas as opções válidas
    todas_opcoes = []
    for categoria, sistemas in sistemas_validos.items():
        todas_opcoes.extend(sistemas)

    # Separar entrada
    sistemas_entrada = [s.strip() for s in entrada.replace('\n', ',').split(',') if s.strip()]

    # Fazer fuzzy matching
    sistemas_reconhecidos = []
    for sistema in sistemas_entrada:
        match = fuzzy_match(sistema, todas_opcoes, threshold=0.6)
        if match:
            sistemas_reconhecidos.append(match)
        else:
            # Se não encontrou match, adicionar como está (pode ser sistema novo)
            sistemas_reconhecidos.append(sistema)

    return sistemas_reconhecidos


def parse_operadores(entrada: str, operadores_validos: List[str]) -> List[str]:
    """
    Parse inteligente de operadores com fuzzy matching

    Args:
        entrada: String com operadores separados por vírgula ou números
        operadores_validos: Lista de operadores válidos

    Returns:
        Lista de operadores reconhecidos
    """
    # Separar entrada
    partes = [p.strip() for p in entrada.replace('\n', ',').split(',') if p.strip()]

    operadores_reconhecidos = []
    for parte in partes:
        # Tentar interpretar como número primeiro
        try:
            num = int(parte)
            if 1 <= num <= len(operadores_validos):
                operadores_reconhecidos.append(operadores_validos[num - 1])
                continue
        except ValueError:
            pass

        # Fazer fuzzy matching
        match = fuzzy_match(parte, operadores_validos, threshold=0.6)
        if match:
            operadores_reconhecidos.append(match)
        else:
            # Se não encontrou match, adicionar como está
            operadores_reconhecidos.append(parte)

    return operadores_reconhecidos


def parse_documentos(entrada: str) -> dict:
    """
    Parse estruturado de documentos (entrada/saída)

    Args:
        entrada: String com documentos ou JSON

    Returns:
        Dict com documentos estruturados
    """
    try:
        import json as json_lib
        # Tentar parsear como JSON primeiro
        dados = json_lib.loads(entrada)
        if isinstance(dados, dict) and 'entrada' in dados and 'saida' in dados:
            return dados
        elif isinstance(dados, list):
            # Lista simples, considerar como entrada
            return {
                'entrada': dados,
                'saida': []
            }
    except:
        pass

    # Parse de texto simples
    docs = [d.strip() for d in entrada.replace('\n', ',').split(',') if d.strip()]

    return {
        'entrada': docs,
        'saida': []
    }


def parse_fluxos(entrada: str) -> List[str]:
    """
    Parse de fluxos (entrada ou saída)

    Args:
        entrada: String com fluxos separados por vírgula

    Returns:
        Lista de fluxos
    """
    return [f.strip() for f in entrada.replace('\n', ',').split(',') if f.strip()]
