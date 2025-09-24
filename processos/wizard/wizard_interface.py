from typing import Dict, List
from .validation_wizard import ValidationWizard

class WizardInterface:
    """
    Interface para interação com o wizard de validação
    Conecta o wizard com as views Django
    """
    
    def __init__(self):
        self.wizard = ValidationWizard()
        self.section_titles = {
            'identificacao': 'Identificação do Processo',
            'entrega': 'Entrega e Objetivo', 
            'base_legal': 'Fundamentação Legal',
            'operacao': 'Sistemas e Ferramentas',
            'execucao': 'Etapas de Execução'
        }
    
    def process_wizard_step(self, request_data: Dict) -> Dict:
        """
        Processa um passo do wizard enviado via AJAX
        
        Args:
            request_data: Dados enviados pelo frontend
            
        Returns:
            Dict com response estruturada para o frontend
        """
        section = request_data.get('section')
        data = request_data.get('data', {})
        
        # Validar seção atual
        is_valid, errors = self.wizard.validate_section(section, data)
        
        # Determinar próxima ação
        if is_valid:
            next_action = self._determine_next_action(request_data.get('complete_form_data', {}))
        else:
            next_action = {'type': 'fix_errors', 'section': section}
        
        return {
            'success': is_valid,
            'errors': errors,
            'next_action': next_action,
            'validation_messages': self._generate_user_messages(is_valid, errors)
        }
    
    def _determine_next_action(self, complete_form_data: Dict) -> Dict:
        """Determina próxima ação baseada no estado do formulário"""
        next_field = self.wizard.get_next_required_field(complete_form_data)
        
        if next_field:
            section, field = next_field
            return {
                'type': 'focus_field',
                'section': section,
                'field': field,
                'message': f"Agora vamos preencher o campo '{field}' na seção '{self.section_titles[section]}'"
            }
        else:
            # Todos os campos obrigatórios preenchidos
            is_valid, errors = self.wizard.validate_complete_form(complete_form_data)
            if is_valid:
                return {'type': 'ready_to_generate', 'message': 'Formulário completo! Pronto para gerar POP.'}
            else:
                return {'type': 'has_errors', 'errors': errors}
    
    def _generate_user_messages(self, is_valid: bool, errors: List[str]) -> List[str]:
        """Gera mensagens amigáveis para o usuário"""
        if is_valid:
            return ["Seção validada com sucesso!"]
        
        user_messages = []
        for error in errors:
            # Converter mensagens técnicas em linguagem amigável
            if "é obrigatório" in error:
                field = error.split("'")[1]
                user_messages.append(f"Por favor, preencha o campo {field}")
            elif "mínimo" in error:
                user_messages.append(f"Campo precisa ser mais específico: {error}")
            elif "evite termos genéricos" in error:
                user_messages.append("Tente ser mais específico na descrição")
            else:
                user_messages.append(error)
        
        return user_messages