"""
Modelo Orgao - Representa órgãos da administração pública
"""
from django.db import models


class Orgao(models.Model):
    """
    Representa um órgão da administração pública.

    Responsável por:
    - Isolamento multi-tenancy (cada órgão vê apenas seus dados)
    - Hierarquia organizacional
    - Configurações específicas por órgão
    """

    # Identificação
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código SIORG",
        help_text="Código do órgão no SIORG (Sistema de Informações Organizacionais do Governo Federal)"
    )
    nome = models.CharField(
        max_length=255,
        verbose_name="Nome do Órgão"
    )
    sigla = models.CharField(
        max_length=20,
        verbose_name="Sigla",
        help_text="Ex: AGU, CGU, MEC"
    )

    # Hierarquia
    orgao_pai = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orgaos_filhos',
        verbose_name="Órgão Superior"
    )

    # Tipo
    TIPO_CHOICES = [
        ('federal', 'Federal'),
        ('estadual', 'Estadual'),
        ('municipal', 'Municipal'),
        ('autarquia', 'Autarquia'),
        ('fundacao', 'Fundação'),
        ('empresa_publica', 'Empresa Pública'),
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='federal'
    )

    # Contato
    email = models.EmailField(
        blank=True,
        verbose_name="E-mail institucional"
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone"
    )

    # Configurações
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Órgãos inativos não podem criar novos dados"
    )

    # Auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Órgão"
        verbose_name_plural = "Órgãos"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['sigla']),
        ]

    def __str__(self):
        return f"{self.sigla} - {self.nome}"

    def get_hierarquia(self):
        """Retorna lista de órgãos na hierarquia (do topo até este)"""
        hierarquia = [self]
        pai = self.orgao_pai
        while pai:
            hierarquia.insert(0, pai)
            pai = pai.orgao_pai
        return hierarquia

    def get_hierarquia_display(self):
        """Retorna string com hierarquia (ex: 'AGU > PGF > PGFN')"""
        return ' > '.join([o.sigla for o in self.get_hierarquia()])
