from rest_framework import serializers
from .models import ProcessoMestre, ControleGastos, POP, POPSnapshot

class ProcessoMestreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessoMestre
        fields = '__all__'


# Serializer para ControleGastos
class ControleGastosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControleGastos
        fields = '__all__'


class POPSerializer(serializers.ModelSerializer):
    class Meta:
        model = POP
        fields = '__all__'
        read_only_fields = [
            'uuid','created_at','updated_at','integrity_hash','last_autosave_at',
            'autosave_sequence','last_activity_at','versao'
        ]


class POPAutosaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = POP
        fields = [
            'id','uuid','status','raw_payload','sistemas_utilizados','etapas',
            'documentos_utilizados','fluxos_entrada','fluxos_saida','pontos_atencao',
            'operadores','entrega_esperada','dispositivos_normativos','nome_processo',
            'macroprocesso','codigo_processo','processo_especifico','area_codigo','area_nome'
        ]


class POPSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = POPSnapshot
        fields = '__all__'
        read_only_fields = ['created_at']