import json
from typing import Dict, List, Tuple, Optional
from django.core.exceptions import ValidationError

class ValidationWizard:
    """
    Wizard de validação para garantir completude e conformidade 
    dos dados do processo antes da geração do POP final
    """
    
    def __init__(self):
        self.required_fields = self._define_required_fields()
        self.validation_rules = self._define_validation_rules()
        self.field_dependencies = self._define_field_dependencies()
    
    def _define_required_fields(self) -> Dict[str, List[str]]:
        """Define campos obrigatórios por seção"""
        return {
            'identificacao': [
                'processo',
                'macroprocesso', 
                'objetivo'
            ],
            'entrega': [
                'produto_final',
                'beneficiario'
            ],
            'base_legal': [
                'normas_aplicaveis'
            ],
            'operacao': [
                'sistemas_utilizados',
                'responsaveis'
            ],
            'execucao': [
                'etapas_principais'
            ]
        }
    
    def _define_validation_rules(self) -> Dict[str, Dict]:
        """Define regras de validação específicas"""
        return {
            'processo': {
                'min_length': 10,
                'max_length': 200,
                'forbidden_words': ['processo', 'análise', 'verificação']
            },
            'objetivo': {
                'min_length': 20,
                'max_length': 500
            },
            'produto_final': {
                'min_length': 10,
                'max_length': 300
            },
            'etapas_principais': {
                'min_items': 3,
                'max_items': 50
            },
            'sistemas_utilizados': {
                'min_items': 1,
                'max_items': 10
            }
        }
    
    def _define_field_dependencies(self) -> Dict[str, List[str]]:
        """Define dependências entre campos"""
        return {
            'subprocesso': ['macroprocesso'],
            'atividade': ['subprocesso'],
            'controles': ['riscos_identificados'],
            'plano_mitigacao': ['riscos_identificados']
        }
    
    def validate_section(self, section_name: str, data: Dict) -> Tuple[bool, List[str]]:
        """
        Valida uma seção específica do formulário
        
        Args:
            section_name: Nome da seção (identificacao, entrega, etc.)
            data: Dados da seção para validar
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Verificar campos obrigatórios
        required = self.required_fields.get(section_name, [])
        for field in required:
            if not data.get(field) or str(data[field]).strip() == '':
                errors.append(f"Campo '{field}' é obrigatório")
        
        # Aplicar regras específicas de validação
        for field, value in data.items():
            if field in self.validation_rules:
                field_errors = self._validate_field(field, value)
                errors.extend(field_errors)
        
        # Verificar dependências
        dependency_errors = self._validate_dependencies(data)
        errors.extend(dependency_errors)
        
        return len(errors) == 0, errors
    
    def _validate_field(self, field_name: str, value) -> List[str]:
        """Valida um campo específico baseado nas regras"""
        errors = []
        rules = self.validation_rules.get(field_name, {})
        
        if isinstance(value, str):
            # Validações de string
            if 'min_length' in rules and len(value.strip()) < rules['min_length']:
                errors.append(f"{field_name}: mínimo {rules['min_length']} caracteres")
            
            if 'max_length' in rules and len(value.strip()) > rules['max_length']:
                errors.append(f"{field_name}: máximo {rules['max_length']} caracteres")
            
            if 'forbidden_words' in rules:
                value_lower = value.lower()
                forbidden = [word for word in rules['forbidden_words'] 
                           if word in value_lower]
                if forbidden:
                    errors.append(f"{field_name}: evite termos genéricos como {', '.join(forbidden)}")
        
        elif isinstance(value, list):
            # Validações de lista
            if 'min_items' in rules and len(value) < rules['min_items']:
                errors.append(f"{field_name}: mínimo {rules['min_items']} itens")
            
            if 'max_items' in rules and len(value) > rules['max_items']:
                errors.append(f"{field_name}: máximo {rules['max_items']} itens")
        
        return errors
    
    def _validate_dependencies(self, data: Dict) -> List[str]:
        """Valida dependências entre campos"""
        errors = []
        
        for field, dependencies in self.field_dependencies.items():
            if data.get(field):  # Se campo existe
                for dep in dependencies:
                    if not data.get(dep):
                        errors.append(f"Campo '{field}' requer que '{dep}' esteja preenchido")
        
        return errors
    
    def validate_complete_form(self, form_data: Dict) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Valida o formulário completo antes da geração final
        
        Args:
            form_data: Dados completos do formulário organizados por seção
            
        Returns:
            Tuple[bool, Dict]: (is_valid, errors_by_section)
        """
        all_errors = {}
        all_valid = True
        
        for section, data in form_data.items():
            is_valid, errors = self.validate_section(section, data)
            if not is_valid:
                all_errors[section] = errors
                all_valid = False
        
        # Validações transversais (entre seções)
        cross_section_errors = self._validate_cross_sections(form_data)
        if cross_section_errors:
            all_errors['geral'] = cross_section_errors
            all_valid = False
        
        return all_valid, all_errors
    
    def _validate_cross_sections(self, form_data: Dict) -> List[str]:
        """Validações que cruzam múltiplas seções"""
        errors = []
        
        # Exemplo: verificar consistência entre objetivo e produto final
        identificacao = form_data.get('identificacao', {})
        entrega = form_data.get('entrega', {})
        
        objetivo = identificacao.get('objetivo', '').lower()
        produto = entrega.get('produto_final', '').lower()
        
        # Verificações de consistência semântica básica
        if objetivo and produto:
            # Exemplo de validação: palavras-chave conflitantes
            conflitos = self._detect_semantic_conflicts(objetivo, produto)
            if conflitos:
                errors.append(f"Possível inconsistência entre objetivo e produto final: {conflitos}")
        
        return errors
    
    def _detect_semantic_conflicts(self, objetivo: str, produto: str) -> str:
        """Detecta conflitos semânticos básicos"""
        # Implementação simplificada - pode ser expandida
        verbos_objetivo = ['analisar', 'verificar', 'aprovar', 'processar']
        substantivos_produto = ['análise', 'verificação', 'aprovação', 'processamento']
        
        objetivo_verbs = [v for v in verbos_objetivo if v in objetivo]
        produto_nouns = [s for s in substantivos_produto if s in produto]
        
        if objetivo_verbs and not produto_nouns:
            return "Objetivo indica ação mas produto final não especifica entrega concreta"
        
        return ""
    
    def get_validation_progress(self, form_data: Dict) -> Dict[str, float]:
        """
        Calcula progresso de preenchimento por seção
        
        Returns:
            Dict com percentual de completude por seção
        """
        progress = {}
        
        for section, required_fields in self.required_fields.items():
            section_data = form_data.get(section, {})
            filled_fields = sum(1 for field in required_fields 
                              if section_data.get(field) and str(section_data[field]).strip())
            
            progress[section] = (filled_fields / len(required_fields)) * 100 if required_fields else 100
        
        return progress
    
    def get_next_required_field(self, form_data: Dict) -> Optional[Tuple[str, str]]:
        """
        Identifica o próximo campo obrigatório a ser preenchido
        
        Returns:
            Tuple[str, str]: (section_name, field_name) ou None se tudo preenchido
        """
        for section, required_fields in self.required_fields.items():
            section_data = form_data.get(section, {})
            
            for field in required_fields:
                if not section_data.get(field) or str(section_data[field]).strip() == '':
                    return section, field
        
        return None
    
    def generate_validation_report(self, form_data: Dict) -> Dict:
        """
        Gera relatório completo de validação para debugging/auditoria
        """
        is_valid, errors = self.validate_complete_form(form_data)
        progress = self.get_validation_progress(form_data)
        next_field = self.get_next_required_field(form_data)
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'progress_by_section': progress,
            'overall_progress': sum(progress.values()) / len(progress) if progress else 0,
            'next_required_field': next_field,
            'total_required_fields': sum(len(fields) for fields in self.required_fields.values()),
            'filled_required_fields': sum(len(self.required_fields[section]) * (prog/100) 
                                        for section, prog in progress.items())
        }