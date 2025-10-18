import csv
import os
from django.conf import settings

class ArquiteturaDecipex:
    """Lê e estrutura dados da Arquitetura de Processos DECIPEX"""
    
    def __init__(self):
        self.csv_path = os.path.join(settings.BASE_DIR, 'documentos_teste', 'Arquitetura_DECIPEX_mapeada.csv')
        self.dados = self._ler_csv()
        
    def _ler_csv(self):
        """Lê CSV e retorna lista de dicionários"""
        dados = []
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dados.append(row)
            print(f"[OK] CSV carregado: {len(dados)} linhas")
            return dados
        except Exception as e:
            print(f"[ERROR] Erro ao ler CSV: {e}")
            return []
    
    def obter_macroprocessos_unicos(self):
        """Retorna lista de macroprocessos únicos"""
        macros = set(row['Macroprocesso'] for row in self.dados if row['Macroprocesso'])
        return sorted(list(macros))
    
    def obter_processos_por_macro(self, macroprocesso):
        """Retorna processos de um macroprocesso específico"""
        processos = set(
            row['Processo'] 
            for row in self.dados 
            if row['Macroprocesso'] == macroprocesso and row['Processo']
        )
        return sorted(list(processos))
    
    def obter_subprocessos_por_processo(self, macroprocesso, processo):
        """Retorna subprocessos de um processo específico"""
        subs = set(
            row['Subprocesso']
            for row in self.dados
            if row['Macroprocesso'] == macroprocesso 
            and row['Processo'] == processo
            and row['Subprocesso']
        )
        return sorted(list(subs))
    
    def obter_atividades_por_subprocesso(self, macroprocesso, processo, subprocesso):
        """Retorna atividades de um subprocesso específico"""
        atividades = [
            row['Atividade']
            for row in self.dados
            if row['Macroprocesso'] == macroprocesso
            and row['Processo'] == processo
            and row['Subprocesso'] == subprocesso
            and row['Atividade']
        ]
        return sorted(atividades)
    
    def buscar_atividade_completa(self, nome_atividade):
        """Retorna hierarquia completa de uma atividade pelo nome"""
        for row in self.dados:
            if row['Atividade'].lower() == nome_atividade.lower():
                return {
                    'macroprocesso': row['Macroprocesso'],
                    'processo': row['Processo'],
                    'subprocesso': row['Subprocesso'],
                    'atividade': row['Atividade'],
                    'aba': row.get('Aba', '')
                }
        return None