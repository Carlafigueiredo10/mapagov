"""
Models para P6 - Plano de Ação e Controles

Gestão completa de ações: mitigação de riscos, implementação de oportunidades
e planejamento estratégico (incluindo mobilização para mapeamento).
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class PlanoAcao(models.Model):
    """
    Plano de Ação - Container de múltiplas ações relacionadas

    Exemplos:
    - Mobilização para mapeamento de processos
    - Implementação de oportunidades identificadas
    - Mitigação de riscos críticos
    - Preparação para auditoria
    """

    TIPO_CHOICES = [
        ('mobilizacao', 'Mobilização para Mapeamento'),
        ('riscos', 'Mitigação de Riscos'),
        ('oportunidades', 'Implementação de Oportunidades'),
        ('auditoria', 'Preparação para Auditoria'),
        ('treinamento', 'Treinamento de Equipe'),
        ('implantacao_sistema', 'Implantação de Sistema'),
        ('conformidade', 'Adequação de Conformidade'),
        ('outro', 'Outro')
    ]

    # Identificação
    titulo = models.CharField(
        max_length=200,
        help_text="Título do plano de ação (ex: 'Mobilização CGRIS - Q1 2026')"
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        default='mobilizacao'
    )

    # Dados principais
    objetivo = models.TextField(
        help_text="Objetivo geral do plano de ação"
    )
    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada do plano"
    )

    # Métricas
    prazo_total_dias = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Prazo total em dias"
    )
    custo_total_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Custo total estimado em R$"
    )
    roi_esperado = models.TextField(
        blank=True,
        help_text="ROI esperado (ex: '45 atividades mapeadas', '120h/mês economizadas')"
    )

    # Contexto organizacional
    area = models.CharField(
        max_length=100,
        blank=True,
        help_text="Área responsável (ex: 'CGRIS', 'CGCAF')"
    )

    # Rastreabilidade
    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='planos_acao_criados'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # Estado do plano
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('ativo', 'Ativo'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado')
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='rascunho'
    )

    # Metadados
    session_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID da sessão de chat que criou este plano"
    )

    class Meta:
        db_table = 'planos_acao'
        verbose_name = 'Plano de Ação'
        verbose_name_plural = 'Planos de Ação'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"

    @property
    def total_acoes(self):
        """Total de ações no plano"""
        return self.acoes.count()

    @property
    def acoes_concluidas(self):
        """Total de ações concluídas"""
        return self.acoes.filter(status='concluido').count()

    @property
    def percentual_conclusao(self):
        """Percentual de conclusão do plano (0-100)"""
        total = self.total_acoes
        if total == 0:
            return 0
        return int((self.acoes_concluidas / total) * 100)

    @property
    def custo_real_total(self):
        """Soma dos custos reais de todas as ações"""
        return self.acoes.aggregate(
            total=models.Sum('how_much_real')
        )['total'] or Decimal('0.00')


class Acao(models.Model):
    """
    Ação individual dentro de um Plano de Ação

    Estrutura 5W2H:
    - What (O que): Descrição da ação
    - Why (Por que): Justificativa/objetivo
    - Where (Onde): Local de execução
    - When (Quando): Data/prazo
    - Who (Quem): Responsável
    - How (Como): Metodologia/estratégia
    - How Much (Quanto): Custo estimado
    """

    # Relacionamento
    plano = models.ForeignKey(
        PlanoAcao,
        on_delete=models.CASCADE,
        related_name='acoes'
    )

    # Ordem/prioridade
    ordem = models.IntegerField(
        default=0,
        help_text="Ordem de execução (0 = primeira)"
    )

    # 5W2H - WHAT (O que)
    what = models.TextField(
        verbose_name="O que fazer",
        help_text="Descrição da ação a ser realizada"
    )

    # 5W2H - WHY (Por que)
    why = models.TextField(
        verbose_name="Por que fazer",
        help_text="Justificativa e objetivo da ação"
    )

    # 5W2H - WHERE (Onde)
    where = models.CharField(
        max_length=200,
        verbose_name="Onde executar",
        help_text="Local ou setor de execução (ex: 'CGRIS', 'Online', 'Sala de reuniões')"
    )

    # 5W2H - WHEN (Quando)
    when_inicio = models.DateField(
        verbose_name="Data de início",
        null=True,
        blank=True
    )
    when_fim = models.DateField(
        verbose_name="Data de conclusão prevista"
    )
    when_fim_real = models.DateField(
        verbose_name="Data de conclusão real",
        null=True,
        blank=True
    )

    # 5W2H - WHO (Quem)
    who = models.CharField(
        max_length=200,
        verbose_name="Quem é responsável",
        help_text="Nome do responsável ou equipe"
    )
    who_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acoes_responsaveis',
        help_text="Usuário responsável (se cadastrado no sistema)"
    )

    # 5W2H - HOW (Como)
    how = models.TextField(
        verbose_name="Como fazer",
        help_text="Metodologia, estratégia ou passos para executar"
    )

    # 5W2H - HOW MUCH (Quanto custa)
    how_much_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Custo estimado (R$)"
    )
    how_much_real = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Custo real (R$)",
        blank=True
    )

    # Estado
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('andamento', 'Em Andamento'),
        ('revisao', 'Em Revisão'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado')
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )

    # Observações
    observacoes = models.TextField(
        blank=True,
        help_text="Observações gerais sobre a ação"
    )
    bloqueadores = models.TextField(
        blank=True,
        help_text="Bloqueadores ou impedimentos identificados"
    )

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'acoes'
        verbose_name = 'Ação'
        verbose_name_plural = 'Ações'
        ordering = ['plano', 'ordem', 'when_fim']

    def __str__(self):
        return f"[{self.plano.titulo}] {self.what[:50]}"

    @property
    def esta_atrasada(self):
        """Verifica se a ação está atrasada"""
        from django.utils import timezone
        if self.status == 'concluido':
            return False
        return self.when_fim < timezone.now().date()

    @property
    def dias_ate_prazo(self):
        """Dias restantes até o prazo (negativo se atrasado)"""
        from django.utils import timezone
        delta = self.when_fim - timezone.now().date()
        return delta.days

    @property
    def variacao_custo(self):
        """Variação entre custo estimado e real"""
        if self.how_much_real == 0:
            return Decimal('0.00')
        return self.how_much_real - self.how_much_estimado


class ComentarioAcao(models.Model):
    """
    Comentários e atualizações sobre uma ação

    Permite rastreabilidade e comunicação sobre o andamento
    """

    acao = models.ForeignKey(
        Acao,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    # Tipo de comentário
    TIPO_CHOICES = [
        ('atualizacao', 'Atualização de Status'),
        ('alerta', 'Alerta/Problema'),
        ('observacao', 'Observação Geral')
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='observacao'
    )

    class Meta:
        db_table = 'comentarios_acao'
        verbose_name = 'Comentário de Ação'
        verbose_name_plural = 'Comentários de Ações'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Comentário de {self.autor.username} em {self.acao}"
