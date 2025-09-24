from django.db import models
from django.db import models

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
    processo_mestre = models.ForeignKey(ProcessoMestre, on_delete=models.PROTECT, verbose_name="Identificação do Processo")
    
    # Controle Administrativo (começando com os campos simples)
    versao = models.PositiveIntegerField(default=1, verbose_name="Versão")
    mes_ano = models.CharField(max_length=7, verbose_name="Mês/Ano de Referência (MM/YYYY)")
    data_aprovacao = models.DateField(null=True, blank=True, verbose_name="Data de Aprovação")
    
    # Entrega Esperada
    entrega_esperada = models.TextField(verbose_name="Entrega Esperada da Atividade")

    # (Vamos adicionar os outros campos mais complexos, como a lista de tarefas, depois)

    def __str__(self):
        return f"POP para: {self.processo_mestre.atividade} (v{self.versao})"


# Modelo para Controle de Gastos
class ControleGastos(models.Model):
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data = models.DateField(verbose_name="Data")
    categoria = models.CharField(max_length=100, verbose_name="Categoria")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} em {self.data} ({self.categoria})"