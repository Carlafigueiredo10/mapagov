from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import hashlib
import json

# Novos models FASE 1 (arquitetura refatorada)
from processos.models_new.orgao import Orgao
from processos.models_new.chat_session import ChatSession
from processos.models_new.chat_message import ChatMessage

# Novos models FASE 2 (Security & RBAC)
from processos.models_new.rbac import Role, Permission, RolePermission, UserRole
from processos.models_new.audit_log import AuditLog, SecurityEvent

# Auth & Access Control
from processos.models_auth import UserProfile, AccessApproval

# Models Analise de Riscos (PR2)
from processos.models_analise_riscos import (
    AnaliseRiscos,
    RiscoIdentificado,
    RespostaRisco,
    AnaliseSnapshot,
    MotivoSnapshot,
)

class ProcessoMestre(models.Model):
    codigo_arquitetura = models.CharField(max_length=100, unique=True, verbose_name="Código da Arquitetura")
    macroprocesso = models.CharField(max_length=255, verbose_name="Macroprocesso")
    processo = models.CharField(max_length=255, verbose_name="Processo")
    subprocesso = models.CharField(max_length=255, verbose_name="Subprocesso")
    atividade = models.CharField(max_length=255, verbose_name="Atividade")

    def __str__(self):
        return f"{self.codigo_arquitetura} - {self.atividade}"
# (o código do ProcessoMestre continua aqui em cima)


class POP(models.Model):
    # Identificação e Controle
    session_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID da Sessão")
    processo_mestre = models.ForeignKey(ProcessoMestre, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Identificação do Processo")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="UUID", help_text="Identificador imutável do POP gerado no momento da criação")
    area = models.ForeignKey('Area', on_delete=models.PROTECT, null=True, blank=True, related_name='pops', verbose_name="Área Organizacional")

    # Dados Básicos do Processo
    nome_usuario = models.CharField(max_length=255, verbose_name="Nome do Usuário", default="admin")
    area_codigo = models.CharField(max_length=50, null=True, blank=True, verbose_name="Código da Área")
    area_nome = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nome da Área")
    macroprocesso = models.CharField(max_length=255, null=True, blank=True, verbose_name="Macroprocesso")
    codigo_processo = models.CharField(max_length=50, null=True, blank=True, verbose_name="Código do Processo")
    nome_processo = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nome do Processo")
    processo_especifico = models.CharField(max_length=255, null=True, blank=True, verbose_name="Processo Específico")
    
    # Entrega e Conformidade
    entrega_esperada = models.TextField(null=True, blank=True, verbose_name="Entrega Esperada da Atividade")
    dispositivos_normativos = models.TextField(null=True, blank=True, verbose_name="Dispositivos Normativos")
    
    # Recursos e Operação
    sistemas_utilizados = models.JSONField(default=list, verbose_name="Sistemas Utilizados")
    operadores = models.TextField(null=True, blank=True, verbose_name="Operadores")
    pontos_atencao = models.TextField(null=True, blank=True, verbose_name="Pontos de Atenção")
    
    # Etapas e Fluxos
    etapas = models.JSONField(default=list, verbose_name="Etapas do Processo")
    documentos_utilizados = models.JSONField(default=list, verbose_name="Documentos Utilizados")
    fluxos_entrada = models.JSONField(default=list, verbose_name="Fluxos de Entrada")
    fluxos_saida = models.JSONField(default=list, verbose_name="Fluxos de Saída")
    
    # Controle Administrativo
    versao = models.PositiveIntegerField(default=1, verbose_name="Versão")
    mes_ano = models.CharField(max_length=7, null=True, blank=True, verbose_name="Mês/Ano de Referência (MM/YYYY)")
    data_aprovacao = models.DateField(null=True, blank=True, verbose_name="Data de Aprovação")
    
    # Auditoria
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Criado por")
    from django.utils import timezone
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    is_completo = models.BooleanField(default=False, verbose_name="POP Completo")
    is_deleted = models.BooleanField(default=False, verbose_name="Excluído (soft delete)")
    integrity_hash = models.CharField(max_length=64, null=True, blank=True, verbose_name="Hash de Integridade (SHA256)")

    # Autosave / atividade
    last_autosave_at = models.DateTimeField(null=True, blank=True, verbose_name="Último Auto-Save")
    autosave_sequence = models.PositiveIntegerField(default=0, verbose_name="Sequência de Auto-Save")
    from django.utils import timezone
    last_activity_at = models.DateTimeField(default=timezone.now, verbose_name="Última Atividade")

    status = models.CharField(
        max_length=30,
        choices=[
            ("draft", "Rascunho"),
            ("published", "Publicado"),
            ("archived", "Arquivado"),
        ],
        default="draft",
        verbose_name="Status"
    )

    raw_payload = models.JSONField(null=True, blank=True, verbose_name="Payload Bruto", help_text="Conteúdo bruto recebido do frontend para reconstrução ou depuração")
    
    class Meta:
        verbose_name = "Procedimento Operacional Padrão"
        verbose_name_plural = "Procedimentos Operacionais Padrão"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_processo'],
                condition=models.Q(is_deleted=False) & ~models.Q(codigo_processo=None) & ~models.Q(codigo_processo=''),
                name='unique_cap_ativo',
            ),
        ]

    def __str__(self):
        nome = self.nome_processo or "POP em Andamento"
        return f"{nome} - {self.nome_usuario} (v{self.versao})"
    
    def get_dados_completos(self):
        """Retorna todos os dados do POP em formato dict"""
        return {
            'nome_usuario': self.nome_usuario,
            'area': {
                'codigo': self.area_codigo,
                'nome': self.area_nome
            },
            'macroprocesso': self.macroprocesso,
            'codigo_processo': self.codigo_processo,
            'nome_processo': self.nome_processo,
            'processo_especifico': self.processo_especifico,
            'entrega_esperada': self.entrega_esperada,
            'dispositivos_normativos': self.dispositivos_normativos,
            'sistemas': self.sistemas_utilizados,
            'operadores': self.operadores,
            'pontos_atencao': self.pontos_atencao,
            'etapas': self.etapas,
            'documentos_utilizados': self.documentos_utilizados,
            'fluxos_entrada': self.fluxos_entrada,
            'fluxos_saida': self.fluxos_saida,
            'data_criacao': self.created_at.strftime("%d/%m/%Y %H:%M") if self.created_at else None
        }

    def compute_integrity_hash(self):
        base_dict = self.get_dados_completos()
        base_dict['versao'] = self.versao
        base_dict['status'] = self.status
        payload_bytes = json.dumps(base_dict, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return hashlib.sha256(payload_bytes).hexdigest()

    def create_snapshot(self, autosave=False):
        """Cria um snapshot persistente do estado atual"""
        integrity = self.compute_integrity_hash()
        self.integrity_hash = integrity
        payload = self.get_dados_completos()
        payload['status'] = self.status
        payload['versao'] = self.versao
        payload['uuid'] = str(self.uuid)
        last_snapshot = self.snapshots.order_by('-sequence').first()
        next_seq = (last_snapshot.sequence + 1) if last_snapshot else 1
        return self.snapshots.create(
            sequence=next_seq,
            versao=self.versao,
            autosave_sequence=self.autosave_sequence,
            status=self.status,
            integrity_hash=integrity,
            payload=payload
        )

    def save(self, *args, **kwargs):
        creating = self._state.adding
        # Capturar estado antigo para auditoria
        old_values = {}
        if not creating and self.pk:
            try:
                old = POP.objects.get(pk=self.pk)
                audit_fields = [
                    'nome_processo','macroprocesso','codigo_processo','processo_especifico',
                    'entrega_esperada','dispositivos_normativos','sistemas_utilizados','operadores',
                    'pontos_atencao','etapas','documentos_utilizados','fluxos_entrada','fluxos_saida','status'
                ]
                for f in audit_fields:
                    old_values[f] = getattr(old, f)
            except POP.DoesNotExist:
                pass

        # Atualizar last_activity_at sempre que salvar (atividade manual ou autosave)
        self.last_activity_at = timezone.now()
        if not self.integrity_hash:
            try:
                self.integrity_hash = self.compute_integrity_hash()
            except Exception:
                pass
        super().save(*args, **kwargs)

        # Registrar diffs
        if not creating and old_values:
            from django.forms.models import model_to_dict
            new_values = {}
            for k in old_values.keys():
                new_values[k] = getattr(self, k)
            for field, old_val in old_values.items():
                new_val = new_values.get(field)
                if old_val != new_val:
                    try:
                        POPChangeLog.objects.create(
                            pop=self,
                            user=self.created_by,  # Simplificação: autor original; futuro: user corrente via contexto
                            field_name=field,
                            old_value=old_val,
                            new_value=new_val,
                            autosave_sequence=self.autosave_sequence
                        )
                    except Exception:
                        pass


class POPSnapshot(models.Model):
    pop = models.ForeignKey(POP, on_delete=models.CASCADE, related_name='snapshots', verbose_name="POP")
    from django.utils import timezone
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Criado em")
    sequence = models.PositiveIntegerField(default=1, verbose_name="Sequência")
    versao = models.PositiveIntegerField(verbose_name="Versão do POP no Momento")
    autosave_sequence = models.PositiveIntegerField(default=0, verbose_name="Sequência de Auto-Save no Momento")
    status = models.CharField(max_length=30, verbose_name="Status no Momento")
    integrity_hash = models.CharField(max_length=64, null=True, blank=True, verbose_name="Hash de Integridade")
    payload = models.JSONField(verbose_name="Dados Serializados do POP")
    milestone = models.BooleanField(default=False, verbose_name="Marco (Milestone)")
    milestone_label = models.CharField(max_length=120, null=True, blank=True, verbose_name="Rótulo do Marco")

    class Meta:
        verbose_name = "Snapshot de POP"
        verbose_name_plural = "Snapshots de POP"
        ordering = ['-created_at']

    def __str__(self):
        return f"Snapshot POP {self.pop_id} seq {self.sequence} v{self.versao}"


class POPChangeLog(models.Model):
    pop = models.ForeignKey(POP, on_delete=models.CASCADE, related_name='change_logs', verbose_name="POP")
    from django.utils import timezone
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Registrado em")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Usuário")
    field_name = models.CharField(max_length=100, verbose_name="Campo")
    old_value = models.JSONField(null=True, blank=True, verbose_name="Valor Anterior")
    new_value = models.JSONField(null=True, blank=True, verbose_name="Novo Valor")
    diff_text = models.TextField(null=True, blank=True, verbose_name="Diff Textual")
    autosave_sequence = models.PositiveIntegerField(default=0, verbose_name="Sequência de Auto-Save")

    class Meta:
        verbose_name = "Log de Alteração de POP"
        verbose_name_plural = "Logs de Alteração de POP"
        ordering = ['-created_at']

    def __str__(self):
        return f"Change {self.field_name} POP {self.pop_id} em {self.created_at}"


# ============================================================================
# HELENA SESSION - Persistência de Estado no Banco (Fase 1: Escalabilidade)
# ============================================================================

class HelenaSession(models.Model):
    """
    LEGADO (Fase 1) — Sessão de conversa simplificada.

    Usado por: views.py (chat_api_view, pop_draft_save)
    Substituto planejado: ChatSession (processos.models_new.chat_session)

    ChatSession (Fase 2) é usado por HelenaCore/chat_v2 e possui
    multi-tenancy por órgão, versionamento de agentes e estados JSONB
    por produto. HelenaSession será removido quando chat_v1 for desativado.
    """
    session_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="ID da Sessão",
        help_text="Identificador único da sessão (UUID gerado pelo frontend)"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
        help_text="Usuário autenticado (opcional para sessões anônimas)"
    )

    # Estado da conversa
    produto = models.CharField(
        max_length=50,
        default='gerador_pop',
        verbose_name="Produto Helena",
        help_text="Qual produto: gerador_pop, fluxograma, analise_riscos, etc"
    )
    estado = models.CharField(
        max_length=50,
        default='nome',
        verbose_name="Estado Atual",
        help_text="Estado da máquina de estados: nome, area, arquitetura, campos, etc"
    )
    dados = models.JSONField(
        default=dict,
        verbose_name="Dados da Sessão",
        help_text="Estado completo serializado: nome_usuario, sistemas_selecionados, etapas, etc"
    )

    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizada em")
    last_activity_at = models.DateTimeField(default=timezone.now, verbose_name="Última Atividade")
    is_active = models.BooleanField(default=True, verbose_name="Sessão Ativa")

    # Vínculo com POP (se aplicável)
    pop = models.ForeignKey(
        POP,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='helena_sessions',
        verbose_name="POP Vinculado"
    )

    # Auditoria e Debug
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP do Cliente")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent")

    class Meta:
        verbose_name = "Sessão Helena"
        verbose_name_plural = "Sessões Helena"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['is_active', 'updated_at']),
            models.Index(fields=['user', 'produto']),
        ]

    def __str__(self):
        usuario = self.user.username if self.user else self.dados.get('nome_usuario', 'Anônimo')
        return f"Helena {self.produto} - {usuario} ({self.estado})"

    def atualizar_atividade(self):
        """Atualiza timestamp de última atividade"""
        self.last_activity_at = timezone.now()
        self.save(update_fields=['last_activity_at'])

    def marcar_inativa(self):
        """Marca sessão como inativa (usuário finalizou ou abandonou)"""
        self.is_active = False
        self.save(update_fields=['is_active'])

    @classmethod
    def limpar_sessoes_antigas(cls, dias=30):
        """Remove sessões inativas há mais de N dias"""
        from datetime import timedelta
        limite = timezone.now() - timedelta(days=dias)
        return cls.objects.filter(
            is_active=False,
            updated_at__lt=limite
        ).delete()

    @classmethod
    def obter_ou_criar(cls, session_id, produto='gerador_pop', user=None):
        """Factory method para obter sessão existente ou criar nova"""
        session, created = cls.objects.get_or_create(
            session_id=session_id,
            defaults={
                'produto': produto,
                'estado': 'nome',
                'dados': {},
                'user': user
            }
        )
        if not created:
            session.atualizar_atividade()
        return session, created


# ============================================================================
# POP DRAFT - Rascunho do wizard (independente do POP publicado)
# ============================================================================

class PopDraft(models.Model):
    """
    Rascunho do POP em andamento.

    Persiste o estado do wizard para que o usuário possa pausar e retomar.
    Independente do modelo POP final — draft nunca aparece no catálogo.
    Ao publicar, o draft é transformado em POP (pop_versions) e excluído.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='pop_drafts',
        verbose_name="Usuário"
    )
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="ID da Sessão",
        help_text="Session ID do frontend (fallback quando user é null)"
    )
    area = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Área organizacional"
    )
    process_code = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Código do processo (ex: 7.1.1.1)"
    )
    etapa_atual = models.CharField(
        max_length=50,
        default='nome_usuario',
        verbose_name="Etapa atual do wizard"
    )
    payload_json = models.JSONField(
        default=dict,
        verbose_name="Dados coletados",
        help_text="Tudo que o usuário já respondeu (estado da state machine)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rascunho POP"
        verbose_name_plural = "Rascunhos POP"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', '-updated_at']),
        ]

    def __str__(self):
        nome = self.payload_json.get('nome_usuario', 'Anônimo')
        return f"Draft POP - {nome} ({self.etapa_atual}) - {self.updated_at:%d/%m %H:%M}"


# ============================================================================
# AREA ORGANIZACIONAL - Promovida de CSV para model Django
# ============================================================================

class Area(models.Model):
    """
    Área organizacional da DECIPEX (ex.: CGBEN, CGRIS, DIGEP-RO).
    Dados iniciais carregados de documentos_base/areas_organizacionais.csv.
    Manter sincronizado via: python manage.py sync_areas_from_csv
    """
    codigo = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    nome_curto = models.CharField(max_length=100, verbose_name="Nome Curto")
    slug = models.SlugField(max_length=30, unique=True, verbose_name="Slug",
                            help_text="URL-safe: cgben, digep-ro, etc.")
    prefixo = models.CharField(max_length=10, verbose_name="Prefixo numérico")
    ordem = models.FloatField(default=0, verbose_name="Ordem de exibição")
    ativo = models.BooleanField(default=True, verbose_name="Ativa")
    descricao = models.TextField(blank=True, default="", verbose_name="Descrição")
    area_pai = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subareas', verbose_name="Área Pai"
    )
    tem_subareas = models.BooleanField(default=False, verbose_name="Tem subáreas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizada em")

    class Meta:
        verbose_name = "Área Organizacional"
        verbose_name_plural = "Áreas Organizacionais"
        ordering = ['ordem']

    def __str__(self):
        return f"{self.codigo} - {self.nome_curto}"


# ============================================================================
# POP VERSION - Versão publicada imutável (publish-driven)
# ============================================================================

class PopVersion(models.Model):
    """
    Versão publicada e imutável de um POP.
    Criada no momento do publish. Armazena snapshot congelado dos dados.
    Diferente de POPSnapshot (autosave-driven, efêmero).
    """
    pop = models.ForeignKey(POP, on_delete=models.CASCADE, related_name='versions', verbose_name="POP")
    versao = models.PositiveIntegerField(verbose_name="Número da versão")
    payload = models.JSONField(verbose_name="Dados completos congelados")
    integrity_hash = models.CharField(max_length=64, verbose_name="Hash SHA256")
    published_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Publicado por"
    )
    published_at = models.DateTimeField(default=timezone.now, verbose_name="Publicado em")
    motivo = models.TextField(blank=True, default="", verbose_name="Motivo da publicação")
    is_current = models.BooleanField(default=True, verbose_name="Versão corrente?")

    class Meta:
        verbose_name = "Versão Publicada de POP"
        verbose_name_plural = "Versões Publicadas de POP"
        ordering = ['-versao']
        constraints = [
            models.UniqueConstraint(
                fields=['pop', 'versao'],
                name='unique_pop_version',
            ),
        ]

    def __str__(self):
        return f"POP {self.pop_id} v{self.versao}"


# Modelo para Controle de Gastos
class ControleGastos(models.Model):
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data = models.DateField(verbose_name="Data")
    categoria = models.CharField(max_length=100, verbose_name="Categoria")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} em {self.data} ({self.categoria})"