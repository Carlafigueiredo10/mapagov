"""
Controle de índices para CP (Código de Produto).

Tabela separada do ControleIndices (CAP) — independência total.
"""
from django.db import models


class ControleIndicesProduto(models.Model):
    """
    Controla próximo índice de sequência por (área, produto).
    Anti race-condition para geração de CP.

    Exemplo:
    - (COATE, 01): último_indice = 3 → próximo CP será 03.01.004
    - (DIGEP-RO, 03): último_indice = 1 → próximo CP será 05.01.03.002
    """
    area_codigo = models.CharField(max_length=10)
    produto_codigo = models.CharField(max_length=2)
    ultimo_indice = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'controle_indices_produto'
        verbose_name = 'Controle de Índices (Produto)'
        verbose_name_plural = 'Controles de Índices (Produto)'
        constraints = [
            models.UniqueConstraint(
                fields=['area_codigo', 'produto_codigo'],
                name='unique_area_produto',
            ),
        ]

    def __str__(self):
        return f"{self.area_codigo}/{self.produto_codigo}: {self.ultimo_indice}"
