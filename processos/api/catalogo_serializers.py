from rest_framework import serializers
from processos.models import Area, POP, PopVersion


class AreaSerializer(serializers.ModelSerializer):
    pop_count = serializers.IntegerField(read_only=True, default=0)
    subareas = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = [
            'id', 'codigo', 'nome', 'nome_curto', 'slug', 'prefixo',
            'ordem', 'ativo', 'descricao', 'area_pai', 'tem_subareas',
            'pop_count', 'subareas',
        ]

    def get_subareas(self, obj):
        if obj.tem_subareas:
            children = obj.subareas.filter(ativo=True).order_by('ordem')
            return AreaSerializer(children, many=True, context=self.context).data
        return []


class POPListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagem de catalogo (sem JSONFields pesados)."""
    area_nome = serializers.CharField(source='area.nome_curto', default='')
    area_slug = serializers.CharField(source='area.slug', default='')

    class Meta:
        model = POP
        fields = [
            'id', 'uuid', 'codigo_processo', 'nome_processo',
            'macroprocesso', 'area_nome', 'area_slug',
            'status', 'versao', 'created_at', 'updated_at',
        ]


class POPDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhe do POP."""
    area_detail = AreaSerializer(source='area', read_only=True)

    class Meta:
        model = POP
        exclude = ['raw_payload']
        read_only_fields = [
            'uuid', 'created_at', 'updated_at', 'integrity_hash',
            'last_autosave_at', 'autosave_sequence', 'last_activity_at',
        ]


class PopVersionSerializer(serializers.ModelSerializer):
    published_by_name = serializers.CharField(
        source='published_by.username', default='', read_only=True
    )

    class Meta:
        model = PopVersion
        fields = [
            'versao', 'published_at', 'motivo', 'is_current',
            'integrity_hash', 'published_by_name', 'payload',
        ]
        read_only_fields = fields
