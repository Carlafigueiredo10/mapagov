"""
Modelos de domínio - representação pura de entidades de negócio
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Subetapa:
    """Subetapa dentro de um cenário condicional"""
    numero: str
    descricao: str

    def to_dict(self) -> Dict[str, str]:
        return {"numero": self.numero, "descricao": self.descricao}


@dataclass
class Cenario:
    """Cenário condicional de uma etapa (ex: 'Documentação completa', 'Documentação incompleta')"""
    numero: str
    descricao: str
    subetapas: List[Subetapa] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "numero": self.numero,
            "descricao": self.descricao,
            "subetapas": [s.to_dict() for s in self.subetapas]
        }


@dataclass
class Etapa:
    """Etapa de um processo (linear ou condicional)"""
    numero: str
    descricao: str
    operador: str
    detalhes: List[str] = field(default_factory=list)

    # Campos para etapas condicionais (opcionais)
    tipo: Optional[str] = None  # "condicional" ou None
    tipo_condicional: Optional[str] = None  # "binario" ou "multiplos"
    antes_decisao: Optional[Dict[str, str]] = None  # {"numero": "1.1", "descricao": "..."}
    cenarios: List[Cenario] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para formato esperado pelo frontend/backend"""
        base = {
            "numero": self.numero,
            "descricao": self.descricao,
            "operador": self.operador,
        }

        if self.tipo == "condicional":
            return {
                **base,
                "tipo": "condicional",
                "tipo_condicional": self.tipo_condicional,
                "antes_decisao": self.antes_decisao,
                "cenarios": [c.to_dict() for c in self.cenarios]
            }
        else:
            return {**base, "detalhes": self.detalhes}
