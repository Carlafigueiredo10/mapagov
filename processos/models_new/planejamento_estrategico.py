"""
Models para PE - Planejamento Estratégico

Sistema completo de planejamento estratégico com suporte a múltiplos modelos:
- Tradicional (Missão, Visão, Valores)
- BSC Público (4 perspectivas)
- OKR (Objectives and Key Results)
- SWOT/FOFA (Análise situacional)
- Planejamento por Cenários
- 5W2H (Plano de Ação Tático)
- Hoshin Kanri (Desdobramento em cascata)
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import json


class PlanejamentoEstrategico(models.Model):
    """
    Planejamento Estratégico - Container principal

    Suporta múltiplos modelos através de estrutura flexível JSONField
    """

    MODELO_CHOICES = [
        ('tradicional', 'Planejamento Estratégico Tradicional'),
        ('bsc', 'Balanced Scorecard Público'),
        ('okr', 'Objectives and Key Results (OKR)'),
        ('swot', 'Análise SWOT/FOFA'),
        ('cenarios', 'Planejamento por Cenários'),
        ('5w2h', 'Plano de Ação 5W2H'),
        ('hoshin', 'Hoshin Kanri'),
    ]

    MATURIDADE_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
    ]

    HORIZONTE_CHOICES = [
        ('curto', 'Curto Prazo (até 1 ano)'),
        ('medio', 'Médio Prazo (1-2 anos)'),
        ('longo', 'Longo Prazo (3+ anos)'),
    ]

    STATUS_CHOICES = [
        ('diagnostico', 'Em Diagnóstico'),
        ('construcao', 'Em Construção'),
        ('revisao', 'Em Revisão'),
        ('aprovado', 'Aprovado'),
        ('vigente', 'Vigente'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]

    # ========================================================================
    # IDENTIFICAÇÃO E CONTEXTO
    # ========================================================================

    titulo = models.CharField(
        max_length=200,
        help_text="Título do planejamento (ex: 'PE CGRIS 2025-2027')"
    )

    modelo = models.CharField(
        max_length=20,
        choices=MODELO_CHOICES,
        help_text="Modelo/metodologia utilizada"
    )

    descricao = models.TextField(
        blank=True,
        help_text="Descrição geral do planejamento"
    )

    # Contexto organizacional
    orgao = models.CharField(
        max_length=200,
        blank=True,
        help_text="Órgão/Entidade (ex: 'INSS', 'Ministério da Economia')"
    )

    unidade = models.CharField(
        max_length=200,
        blank=True,
        help_text="Unidade específica (ex: 'CGRIS', 'DECIPEX')"
    )

    escopo = models.CharField(
        max_length=100,
        choices=[
            ('institucional', 'Institucional (órgão completo)'),
            ('unidade', 'Unidade/Departamento'),
            ('projeto', 'Projeto/Programa específico'),
            ('outro', 'Outro'),
        ],
        default='unidade'
    )

    # ========================================================================
    # DIAGNÓSTICO (respostas das 5 perguntas)
    # ========================================================================

    diagnostico = models.JSONField(
        default=dict,
        help_text="Respostas do diagnóstico inicial"
    )
    # Estrutura:
    # {
    #   "maturidade": "iniciante|intermediario|avancado",
    #   "horizonte": "curto|medio|longo",
    #   "contexto": "incerteza|medicao|execucao|conformidade",
    #   "equipe": "pequena|media|grande",
    #   "objetivo": "diagnostico|estrategia|operacional|transformacao"
    # }

    maturidade_organizacao = models.CharField(
        max_length=20,
        choices=MATURIDADE_CHOICES,
        blank=True,
        help_text="Nível de maturidade em planejamento estratégico"
    )

    horizonte_temporal = models.CharField(
        max_length=20,
        choices=HORIZONTE_CHOICES,
        blank=True,
        help_text="Horizonte temporal do planejamento"
    )

    # ========================================================================
    # PONTUAÇÃO DE MODELOS (resultado do diagnóstico)
    # ========================================================================

    pontuacao_modelos = models.JSONField(
        default=dict,
        help_text="Pontuação de cada modelo no diagnóstico"
    )
    # Estrutura:
    # {
    #   "tradicional": 8,
    #   "bsc": 12,
    #   "okr": 15,
    #   "swot": 6,
    #   ...
    # }

    modelos_recomendados = models.JSONField(
        default=list,
        help_text="Top 3 modelos recomendados"
    )
    # Estrutura: ["okr", "bsc", "tradicional"]

    # ========================================================================
    # ESTRUTURA DO PLANEJAMENTO (flexível por modelo)
    # ========================================================================

    estrutura = models.JSONField(
        default=dict,
        help_text="Estrutura completa do planejamento (varia por modelo)"
    )
    # Exemplos por modelo:
    #
    # TRADICIONAL:
    # {
    #   "missao": "Garantir seguridade social...",
    #   "visao": "Ser reconhecido como...",
    #   "valores": ["Transparência", "Eficiência", ...],
    #   "objetivos_estrategicos": [
    #     {"titulo": "...", "indicadores": [...], "metas": [...]}
    #   ]
    # }
    #
    # BSC:
    # {
    #   "perspectivas": {
    #     "sociedade": {
    #       "objetivos": [{"titulo": "...", "indicadores": [...]}]
    #     },
    #     "processos": {...},
    #     "aprendizado": {...},
    #     "orcamentaria": {...}
    #   },
    #   "mapa_estrategico": {...}
    # }
    #
    # OKR:
    # {
    #   "trimestre": "Q1 2025",
    #   "objetivos": [
    #     {
    #       "titulo": "Tornar-se referência em atendimento digital",
    #       "resultados_chave": [
    #         {"descricao": "...", "meta": "...", "unidade": "...", "progresso": 0}
    #       ],
    #       "iniciativas": [...]
    #     }
    #   ]
    # }
    #
    # SWOT:
    # {
    #   "forcas": ["Item 1", "Item 2", ...],
    #   "fraquezas": [...],
    #   "oportunidades": [...],
    #   "ameacas": [...],
    #   "estrategias_cruzadas": {
    #     "fo": [...],  # Forças + Oportunidades
    #     "fa": [...],  # Forças + Ameaças
    #     "do": [...],  # Fraquezas + Oportunidades
    #     "da": [...]   # Fraquezas + Ameaças
    #   }
    # }

    # ========================================================================
    # MÉTRICAS E ACOMPANHAMENTO
    # ========================================================================

    percentual_conclusao = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentual de construção do planejamento (0-100%)"
    )

    data_inicio_vigencia = models.DateField(
        null=True,
        blank=True,
        help_text="Data de início da vigência"
    )

    data_fim_vigencia = models.DateField(
        null=True,
        blank=True,
        help_text="Data de término da vigência"
    )

    # ========================================================================
    # METADADOS E GOVERNANÇA
    # ========================================================================

    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='planejamentos_criados'
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='diagnostico'
    )

    # Session management (como P6)
    session_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID da sessão de chat que criou este planejamento"
    )

    # Versioning
    versao = models.IntegerField(
        default=1,
        help_text="Versão do planejamento (incrementa a cada revisão)"
    )

    planejamento_anterior = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisoes',
        help_text="Planejamento anterior (se for uma revisão)"
    )

    # Aprovação
    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planejamentos_aprovados'
    )

    aprovado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    # Tags e categorização
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags para categorização"
    )

    class Meta:
        db_table = 'planejamentos_estrategicos'
        verbose_name = 'Planejamento Estratégico'
        verbose_name_plural = 'Planejamentos Estratégicos'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['modelo', 'status']),
            models.Index(fields=['session_id']),
            models.Index(fields=['orgao', 'unidade']),
        ]

    def __str__(self):
        return f"{self.titulo} ({self.get_modelo_display()})"

    def to_dict(self):
        """Serializa para dict (útil para APIs)"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'modelo': self.modelo,
            'modelo_display': self.get_modelo_display(),
            'descricao': self.descricao,
            'orgao': self.orgao,
            'unidade': self.unidade,
            'escopo': self.escopo,
            'diagnostico': self.diagnostico,
            'estrutura': self.estrutura,
            'percentual_conclusao': self.percentual_conclusao,
            'status': self.status,
            'status_display': self.get_status_display(),
            'criado_por': self.criado_por.username,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat(),
            'versao': self.versao,
        }

    def criar_revisao(self, usuario):
        """Cria uma nova versão do planejamento"""
        nova_versao = PlanejamentoEstrategico.objects.create(
            titulo=f"{self.titulo} (v{self.versao + 1})",
            modelo=self.modelo,
            descricao=self.descricao,
            orgao=self.orgao,
            unidade=self.unidade,
            escopo=self.escopo,
            diagnostico=self.diagnostico,
            maturidade_organizacao=self.maturidade_organizacao,
            horizonte_temporal=self.horizonte_temporal,
            estrutura=self.estrutura.copy(),
            criado_por=usuario,
            versao=self.versao + 1,
            planejamento_anterior=self,
            status='revisao'
        )
        return nova_versao

    def aprovar(self, usuario):
        """Aprova o planejamento"""
        from django.utils import timezone
        self.status = 'aprovado'
        self.aprovado_por = usuario
        self.aprovado_em = timezone.now()
        self.save()

    def ativar_vigencia(self):
        """Ativa a vigência do planejamento"""
        self.status = 'vigente'
        self.save()


class IndicadorEstrategico(models.Model):
    """
    Indicador de desempenho vinculado ao planejamento

    Usado principalmente em modelos Tradicional e BSC
    """

    TIPO_CHOICES = [
        ('eficiencia', 'Eficiência'),
        ('eficacia', 'Eficácia'),
        ('efetividade', 'Efetividade'),
        ('economicidade', 'Economicidade'),
        ('excelencia', 'Excelência'),
    ]

    PERIODICIDADE_CHOICES = [
        ('mensal', 'Mensal'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]

    planejamento = models.ForeignKey(
        PlanejamentoEstrategico,
        on_delete=models.CASCADE,
        related_name='indicadores'
    )

    # Identificação
    codigo = models.CharField(
        max_length=50,
        blank=True,
        help_text="Código do indicador (ex: 'IND-001')"
    )

    nome = models.CharField(
        max_length=200,
        help_text="Nome do indicador"
    )

    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada do indicador"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        help_text="Tipo do indicador"
    )

    # Fórmula e cálculo
    formula = models.TextField(
        blank=True,
        help_text="Fórmula de cálculo do indicador"
    )

    unidade_medida = models.CharField(
        max_length=50,
        help_text="Unidade de medida (ex: '%', 'dias', 'R$')"
    )

    # Metas
    linha_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor inicial (linha de base)"
    )

    meta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Meta a ser alcançada"
    )

    valor_atual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor atual (último medido)"
    )

    # Acompanhamento
    periodicidade = models.CharField(
        max_length=20,
        choices=PERIODICIDADE_CHOICES,
        default='mensal'
    )

    responsavel = models.CharField(
        max_length=200,
        help_text="Nome do responsável pela coleta"
    )

    fonte_dados = models.TextField(
        blank=True,
        help_text="Fonte dos dados para o indicador"
    )

    # Polaridade
    polaridade_positiva = models.BooleanField(
        default=True,
        help_text="True se maior é melhor, False se menor é melhor"
    )

    # Vinculação com estrutura do planejamento
    caminho_estrutura = models.CharField(
        max_length=500,
        blank=True,
        help_text="Caminho JSON no campo estrutura (ex: 'perspectivas.sociedade.objetivos[0]')"
    )

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'indicadores_estrategicos'
        verbose_name = 'Indicador Estratégico'
        verbose_name_plural = 'Indicadores Estratégicos'
        ordering = ['planejamento', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    @property
    def percentual_atingido(self):
        """Calcula percentual de atingimento da meta"""
        if not self.valor_atual or not self.meta:
            return 0

        if self.linha_base:
            delta_meta = self.meta - self.linha_base
            delta_atual = self.valor_atual - self.linha_base
            if delta_meta == 0:
                return 100
            return float((delta_atual / delta_meta) * 100)
        else:
            if self.meta == 0:
                return 0
            return float((self.valor_atual / self.meta) * 100)

    @property
    def status_semaforo(self):
        """Retorna status semáforo (verde/amarelo/vermelho)"""
        perc = self.percentual_atingido
        if perc >= 90:
            return 'verde'
        elif perc >= 70:
            return 'amarelo'
        else:
            return 'vermelho'


class MedicaoIndicador(models.Model):
    """
    Medição periódica de um indicador

    Histórico de valores ao longo do tempo
    """

    indicador = models.ForeignKey(
        IndicadorEstrategico,
        on_delete=models.CASCADE,
        related_name='medicoes'
    )

    data_referencia = models.DateField(
        help_text="Data de referência da medição"
    )

    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Valor medido"
    )

    observacoes = models.TextField(
        blank=True,
        help_text="Observações sobre a medição"
    )

    registrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medicoes_indicadores'
        verbose_name = 'Medição de Indicador'
        verbose_name_plural = 'Medições de Indicadores'
        ordering = ['-data_referencia']
        unique_together = ['indicador', 'data_referencia']

    def __str__(self):
        return f"{self.indicador.codigo} - {self.data_referencia}: {self.valor}"


class ComentarioPlanejamento(models.Model):
    """
    Comentários e anotações sobre o planejamento

    Útil para revisões colaborativas
    """

    planejamento = models.ForeignKey(
        PlanejamentoEstrategico,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )

    autor = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    conteudo = models.TextField()

    # Pode referenciar parte específica da estrutura
    caminho_estrutura = models.CharField(
        max_length=500,
        blank=True,
        help_text="Caminho JSON para comentário específico (ex: 'objetivos[0].indicadores[1]')"
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    # Tipos de comentário
    TIPO_CHOICES = [
        ('sugestao', 'Sugestão'),
        ('questao', 'Questão'),
        ('aprovacao', 'Aprovação'),
        ('ressalva', 'Ressalva'),
        ('observacao', 'Observação'),
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='observacao'
    )

    resolvido = models.BooleanField(
        default=False,
        help_text="Comentário foi resolvido/endereçado"
    )

    class Meta:
        db_table = 'comentarios_planejamento'
        verbose_name = 'Comentário de Planejamento'
        verbose_name_plural = 'Comentários de Planejamento'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Comentário de {self.autor.username} - {self.tipo}"
