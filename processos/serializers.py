from rest_framework import serializers
from .models import ProcessoMestre, ControleGastos

class ProcessoMestreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessoMestre
        fields = '__all__'


# Serializer para ControleGastos
class ControleGastosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControleGastos
        fields = '__all__'