"""
Modelos para Atividades Sugeridas - Sistema de Governança e Evolução do CSV

Permite que usuários sugiram novas atividades quando não encontradas no catálogo oficial,
com rastreabilidade completa e fluxo de validação por gestores.
"""

from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timezone
import hashlib

User = get_user_model()


class ControleIndices(models.Model):
    """
    Controla próximo índice de atividade por área (anti race-condition)

    Exemplo:
    - CGBEN: último_indice = 107 → próximo será 108
    - CGPAG: último_indice = 110 → próximo será 111
    """
    area_codigo = models.CharField(max_length=10, primary_key=True)
    ultimo_indice = models.IntegerField(default=107)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'controle_indices'
        verbose_name = 'Controle de Índices'
        verbose_name_plural = 'Controles de Índices'

    def __str__(self):
        return f"{self.area_codigo}: {self.ultimo_indice}"


class AtividadeSugerida(models.Model):
    """
    Atividade sugerida por usuário (não encontrada no CSV oficial)

    Fluxo:
    1. Usuário descreve atividade → IA não encontra no CSV
    2. IA sugere nova atividade → salva com status='sugerida'
    3. Gestor valida → status='validada' → injeta no CSV
    4. CSV atualizado → status='publicada'
    """

    STATUS_CHOICES = [
        ('sugerida', 'Sugerida'),
        ('validada', 'Validada'),
        ('rejeitada', 'Rejeitada'),
        ('publicada', 'Publicada'),
    ]

    CONFIANCA_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Média'),
        ('baixa', 'Baixa'),
    ]

    # CAP
    cap_provisorio = models.CharField(max_length=50, unique=True)
    cap_oficial = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # Arquitetura
    area_codigo = models.CharField(max_length=10)
    macroprocesso = models.TextField()
    processo = models.TextField()
    subprocesso = models.TextField()
    atividade = models.TextField()
    entrega_esperada = models.TextField()

    # Rastreabilidade (UTC)
    autor_cpf = models.CharField(max_length=14)
    autor_nome = models.CharField(max_length=200)
    autor_area = models.CharField(max_length=10)
    data_sugestao_utc = models.DateTimeField()
    descricao_original = models.TextField()

    # Hash único (anti-duplicata)
    hash_sugestao = models.CharField(max_length=64, unique=True)

    # Validação
    validador_cpf = models.CharField(max_length=14, null=True, blank=True)
    validador_nome = models.CharField(max_length=200, null=True, blank=True)
    data_validacao_utc = models.DateTimeField(null=True, blank=True)
    comentario_validador = models.TextField(null=True, blank=True)

    # Similaridade (sempre salvo, mesmo < 0.8)
    score_similaridade = models.FloatField(null=True, blank=True)
    sugestoes_similares = models.JSONField(default=list, blank=True)
    scores_similares_todos = models.JSONField(default=list, blank=True)

    # Confiança da IA
    confianca = models.CharField(max_length=10, choices=CONFIANCA_CHOICES)

    # Rastreabilidade do fluxo
    origem_fluxo = models.CharField(max_length=30)  # 'match_exato', 'match_fuzzy', 'nova_atividade_ia'
    interacao_id = models.CharField(max_length=50)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'atividades_sugeridas'
        verbose_name = 'Atividade Sugerida'
        verbose_name_plural = 'Atividades Sugeridas'
        ordering = ['-data_sugestao_utc']
        indexes = [
            models.Index(fields=['status'], name='idx_status'),
            models.Index(fields=['area_codigo'], name='idx_area'),
            models.Index(fields=['autor_cpf'], name='idx_autor'),
        ]

    def __str__(self):
        return f"{self.cap_provisorio} - {self.atividade[:50]}..."

    @classmethod
    def gerar_hash_sugestao(cls, macroprocesso, processo, subprocesso, atividade, autor_cpf, timestamp_utc):
        """
        Gera hash único da sugestão (anti-duplicata)
        """
        hash_content = f"{macroprocesso}|{processo}|{subprocesso}|{atividade}|{autor_cpf}|{timestamp_utc.isoformat()}"
        return hashlib.sha256(hash_content.encode()).hexdigest()

    def aprovar(self, validador_user, comentario=None):
        """
        Aprova a sugestão (gestor)
        """
        self.status = 'validada'
        self.validador_cpf = validador_user.cpf if hasattr(validador_user, 'cpf') else 'N/A'
        self.validador_nome = validador_user.get_full_name() or validador_user.username
        self.data_validacao_utc = datetime.now(timezone.utc)
        if comentario:
            self.comentario_validador = comentario
        self.save()

        # Registrar no histórico
        HistoricoAtividade.objects.create(
            atividade=self,
            tipo_evento='aprovacao',
            usuario_cpf=self.validador_cpf,
            usuario_nome=self.validador_nome,
            comentario=comentario or 'Atividade aprovada pelo gestor'
        )

    def rejeitar(self, validador_user, motivo):
        """
        Rejeita a sugestão (gestor)
        """
        self.status = 'rejeitada'
        self.validador_cpf = validador_user.cpf if hasattr(validador_user, 'cpf') else 'N/A'
        self.validador_nome = validador_user.get_full_name() or validador_user.username
        self.data_validacao_utc = datetime.now(timezone.utc)
        self.comentario_validador = motivo
        self.save()

        # Registrar no histórico
        HistoricoAtividade.objects.create(
            atividade=self,
            tipo_evento='rejeicao',
            usuario_cpf=self.validador_cpf,
            usuario_nome=self.validador_nome,
            comentario=motivo
        )


class HistoricoAtividade(models.Model):
    """
    Histórico de alterações de uma atividade sugerida (auditoria completa)
    """

    TIPO_EVENTO_CHOICES = [
        ('criacao', 'Criação'),
        ('edicao', 'Edição'),
        ('aprovacao', 'Aprovação'),
        ('rejeicao', 'Rejeição'),
        ('mesclagem', 'Mesclagem'),
    ]

    atividade = models.ForeignKey(AtividadeSugerida, on_delete=models.CASCADE, related_name='historico')
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    usuario_cpf = models.CharField(max_length=14)
    usuario_nome = models.CharField(max_length=200)
    data_evento_utc = models.DateTimeField(auto_now_add=True)
    alteracoes_json = models.JSONField(default=dict, blank=True)
    comentario = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historico_atividades'
        verbose_name = 'Histórico de Atividade'
        verbose_name_plural = 'Históricos de Atividades'
        ordering = ['-data_evento_utc']
        indexes = [
            models.Index(fields=['atividade'], name='idx_atividade_hist'),
            models.Index(fields=['data_evento_utc'], name='idx_data_evento'),
        ]

    def __str__(self):
        return f"{self.tipo_evento} - {self.atividade.cap_provisorio} - {self.data_evento_utc}"
