"""
Models para Analise de Riscos

v2.0 - Suporta ModoEntrada, contexto estruturado, inferencia de riscos

Tabelas:
- AnaliseRiscos (principal)
- RiscoIdentificado
- RespostaRisco
- AnaliseSnapshot
"""
import uuid
from django.db import models
from django.contrib.auth.models import User

# Imports de modulos NEUTROS (sem dependencia de domain)
from .analise_riscos_enums import (
    StatusAnalise,
    EstrategiaResposta,
    NivelRisco,
    ModoEntrada,
    TipoOrigem,
    GrauConfianca,
    TipoAvaliacao,
    TipoControle,
    ObjetivoControle,
)
from .analise_riscos_matriz import calcular_score, calcular_nivel


# =============================================================================
# CHOICES ESTAVEIS PARA CAMPOS DE MODEL
# =============================================================================
# Usamos tuples estaticas para evitar que mudancas no enum gerem migrations.
# O enum e usado para validacao em codigo; os choices sao para o banco.

CATEGORIA_RISCO_CHOICES = (
    ("OPERACIONAL", "OPERACIONAL"),
    ("FINANCEIRO", "FINANCEIRO"),  # Historico - mantido para compatibilidade
    ("LEGAL", "LEGAL"),
    ("REPUTACIONAL", "REPUTACIONAL"),
    ("TECNOLOGICO", "TECNOLOGICO"),
    ("IMPACTO_DESIGUAL", "IMPACTO_DESIGUAL"),
)


class FonteSugestao(models.TextChoices):
    """Origem da sugestao de risco"""
    USUARIO = "USUARIO", "Usuario"
    HELENA_INFERENCIA = "HELENA_INFERENCIA", "Helena Inferencia"


class MotivoSnapshot(models.TextChoices):
    """Motivo do snapshot"""
    AUTO_ETAPA = "AUTO_ETAPA", "Mudanca de etapa"
    FINALIZACAO = "FINALIZACAO", "Finalizacao da analise"
    EDICAO_RISCO = "EDICAO_RISCO", "Edicao de risco"
    EDICAO_CONTEXTO = "EDICAO_CONTEXTO", "Edicao de contexto"
    MANUAL = "MANUAL", "Snapshot manual"


class AnaliseRiscos(models.Model):
    """Analise de riscos principal"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orgao_id = models.UUIDField(db_index=True)

    # Modo de entrada e tipo do objeto
    modo_entrada = models.CharField(
        max_length=20,
        choices=[(m.value, m.value) for m in ModoEntrada],
        default=ModoEntrada.QUESTIONARIO.value,
    )
    tipo_origem = models.CharField(
        max_length=20,
        choices=[(t.value, t.value) for t in TipoOrigem],
    )

    # origem_id agora e opcional (so obrigatorio quando modo_entrada=ID)
    origem_id = models.UUIDField(null=True, blank=True)

    # Contexto estruturado (Etapa 1 - Bloco A + B)
    # NUNCA sobrescrever - editar gera snapshot
    contexto_estruturado = models.JSONField(
        default=dict,
        blank=True,
        help_text="Bloco A (identificacao) + Bloco B (contexto operacional)",
    )

    # Texto extraido de PDF (quando modo_entrada=PDF)
    texto_extraido = models.TextField(
        blank=True,
        help_text="Texto extraido do PDF para analise",
    )

    # Respostas dos blocos da Etapa 2 (identificacao orientada)
    respostas_blocos = models.JSONField(
        default=dict,
        blank=True,
        help_text="Respostas dos 7 blocos de identificacao de riscos",
    )

    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in StatusAnalise],
        default=StatusAnalise.RASCUNHO.value,
    )
    etapa_atual = models.PositiveSmallIntegerField(default=0)  # Comeca em 0 (entrada)

    # Campos legados (mantidos para compatibilidade)
    questoes_respondidas = models.JSONField(default=dict, blank=True)
    area_decipex = models.CharField(max_length=50, blank=True)

    # Código de Produto SNI (CP)
    codigo_cp = models.CharField(
        max_length=20, null=True, blank=True,
        verbose_name="Código de Produto (CP)",
    )
    produto_codigo = models.CharField(
        max_length=2, default="01",
        verbose_name="Código do tipo de produto",
    )

    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="analises_riscos_criadas",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "processos_analise_riscos"
        verbose_name = "Analise de Riscos"
        verbose_name_plural = "Analises de Riscos"
        indexes = [
            models.Index(fields=["orgao_id", "status"]),
            models.Index(fields=["origem_id"]),
            models.Index(fields=["modo_entrada"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_cp'],
                condition=~models.Q(codigo_cp=None) & ~models.Q(codigo_cp=''),
                name='unique_cp_analise_riscos',
            ),
        ]

    def __str__(self):
        return f"Analise {self.id} - {self.tipo_origem} - {self.status}"


class RiscoIdentificado(models.Model):
    """Risco identificado em uma analise

    Riscos podem ser:
    - Inferidos pelo sistema (fonte_sugestao=HELENA_INFERENCIA)
    - Adicionados manualmente (fonte_sugestao=USUARIO)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orgao_id = models.UUIDField(db_index=True)

    analise = models.ForeignKey(
        AnaliseRiscos,
        on_delete=models.CASCADE,
        related_name="riscos",
    )

    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIA_RISCO_CHOICES,
    )

    # Campos de analise P x I
    # NOTA: null=True permite que riscos fiquem "pendentes de avaliacao"
    # ate o gestor definir P/I explicitamente. Isso evita "tudo medio" por default.
    probabilidade = models.PositiveSmallIntegerField(null=True, blank=True)
    impacto = models.PositiveSmallIntegerField(null=True, blank=True)
    score_risco = models.PositiveSmallIntegerField(editable=False, null=True, blank=True)
    nivel_risco = models.CharField(
        max_length=20,
        choices=[(n.value, n.value) for n in NivelRisco],
        editable=False,
        blank=True,
        default="",
    )

    # Campos de inferencia (quando fonte_sugestao=HELENA_INFERENCIA)
    bloco_origem = models.CharField(
        max_length=20,
        blank=True,
        help_text="Bloco que originou o risco (ex: BLOCO_1)",
    )
    perguntas_acionadoras = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de perguntas que acionaram a regra (ex: ['Q1', 'Q2'])",
    )
    regra_aplicada = models.CharField(
        max_length=100,
        blank=True,
        help_text="Identificador da regra de inferencia aplicada",
    )
    grau_confianca = models.CharField(
        max_length=10,
        choices=[(g.value, g.value) for g in GrauConfianca],
        blank=True,
        help_text="Grau de confianca da inferencia",
    )
    justificativa = models.TextField(
        blank=True,
        help_text="Justificativa rastreavel da inferencia",
    )

    # --- Campos Agatha 3.0 ---
    causas = models.JSONField(
        default=list, blank=True,
        help_text="Lista de causas do evento de risco",
    )
    consequencias = models.JSONField(
        default=list, blank=True,
        help_text="Lista de consequencias do evento de risco",
    )
    controles_existentes = models.JSONField(
        default=list, blank=True,
        help_text="[{descricao, desenho, operacao}] - tripe Agatha",
    )
    tipo_avaliacao = models.CharField(
        max_length=30,
        choices=[(t.value, t.value) for t in TipoAvaliacao],
        default=TipoAvaliacao.RESIDUAL_ATUAL.value,
    )

    # Projecao pos-plano (opcional)
    probabilidade_pos_plano = models.PositiveSmallIntegerField(null=True, blank=True)
    impacto_pos_plano = models.PositiveSmallIntegerField(null=True, blank=True)
    score_pos_plano = models.PositiveSmallIntegerField(
        editable=False, null=True, blank=True,
    )
    nivel_pos_plano = models.CharField(
        max_length=20,
        choices=[(n.value, n.value) for n in NivelRisco],
        editable=False, blank=True, default="",
    )

    fonte_sugestao = models.CharField(
        max_length=20,
        choices=FonteSugestao.choices,
        default=FonteSugestao.USUARIO,
    )
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "processos_risco_identificado"
        verbose_name = "Risco Identificado"
        verbose_name_plural = "Riscos Identificados"
        indexes = [
            models.Index(fields=["orgao_id"]),
            models.Index(fields=["analise", "ativo"]),
            models.Index(fields=["bloco_origem"]),
        ]

    def save(self, *args, **kwargs):
        # Calcula score/nivel apenas se P e I estiverem definidos
        if self.probabilidade is not None and self.impacto is not None:
            self.score_risco = calcular_score(self.probabilidade, self.impacto)
            self.nivel_risco = calcular_nivel(self.score_risco)
        else:
            self.score_risco = None
            self.nivel_risco = ""
        # Calcula projecao pos-plano (se preenchida)
        if self.probabilidade_pos_plano is not None and self.impacto_pos_plano is not None:
            self.score_pos_plano = calcular_score(self.probabilidade_pos_plano, self.impacto_pos_plano)
            self.nivel_pos_plano = calcular_nivel(self.score_pos_plano)
        else:
            self.score_pos_plano = None
            self.nivel_pos_plano = ""
        if not self.orgao_id:
            self.orgao_id = self.analise.orgao_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} ({self.nivel_risco})"


class RespostaRisco(models.Model):
    """Resposta/tratamento para um risco"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orgao_id = models.UUIDField(db_index=True)

    risco = models.ForeignKey(
        RiscoIdentificado,
        on_delete=models.CASCADE,
        related_name="respostas",
    )

    estrategia = models.CharField(
        max_length=20,
        choices=[(e.value, e.value) for e in EstrategiaResposta],
    )
    descricao_acao = models.TextField()
    responsavel_nome = models.CharField(max_length=255)
    responsavel_area = models.CharField(max_length=100)
    prazo = models.DateField(null=True, blank=True)

    # --- Campos Agatha 3.0 (plano de controle) ---
    tipo_controle = models.CharField(
        max_length=20,
        choices=[(t.value, t.value) for t in TipoControle],
        blank=True,
    )
    objetivo_controle = models.CharField(
        max_length=20,
        choices=[(o.value, o.value) for o in ObjetivoControle],
        blank=True,
    )
    como_implementar = models.TextField(blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_conclusao_prevista = models.DateField(null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "processos_resposta_risco"
        verbose_name = "Resposta ao Risco"
        verbose_name_plural = "Respostas aos Riscos"
        indexes = [
            models.Index(fields=["orgao_id"]),
        ]

    def save(self, *args, **kwargs):
        if not self.orgao_id:
            self.orgao_id = self.risco.orgao_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.estrategia} - {self.risco.titulo}"


class AnaliseSnapshot(models.Model):
    """Snapshot de versao da analise"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    analise = models.ForeignKey(
        AnaliseRiscos,
        on_delete=models.CASCADE,
        related_name="snapshots",
    )

    versao = models.PositiveIntegerField()
    dados_completos = models.JSONField()
    motivo_snapshot = models.CharField(
        max_length=30,
        choices=MotivoSnapshot.choices,
    )
    correlation_id = models.CharField(max_length=100, blank=True)

    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="snapshots_criados",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "processos_analise_snapshot"
        verbose_name = "Snapshot de Analise"
        verbose_name_plural = "Snapshots de Analises"
        ordering = ["-versao"]
        indexes = [
            models.Index(fields=["analise", "-versao"]),
        ]

    def __str__(self):
        return f"Snapshot v{self.versao} - {self.analise_id}"
