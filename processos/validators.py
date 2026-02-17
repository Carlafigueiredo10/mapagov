"""Validators customizados — padrao Gov.br de senha."""

import re
from django.core.exceptions import ValidationError


class GovBrPasswordValidator:
    """
    Exige maiuscula, minuscula, numero e simbolo.
    Padrao Gov.br para que o usuario possa reutilizar a mesma senha.
    """

    def validate(self, password, user=None):
        errors = []
        if not re.search(r'[A-Z]', password):
            errors.append('A senha deve conter ao menos uma letra maiuscula.')
        if not re.search(r'[a-z]', password):
            errors.append('A senha deve conter ao menos uma letra minuscula.')
        if not re.search(r'[0-9]', password):
            errors.append('A senha deve conter ao menos um numero.')
        if not re.search(r'[^A-Za-z0-9]', password):
            errors.append('A senha deve conter ao menos um simbolo (!@#$%...).')
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return 'A senha deve conter maiuscula, minuscula, numero e simbolo.'
