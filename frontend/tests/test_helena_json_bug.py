"""
Teste do bug de serialização JSON nas chaves de dados_coletados
"""
import json
import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapagov.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from processos.domain.helena_produtos.helena_etapas import HelenaEtapas

def test_json_serialization():
    helena = HelenaEtapas()

    # Inicializa estado
    estado = helena.inicializar_estado()
    print("Estado inicial (tipo de chaves):", type(list(estado['dados_coletados'].keys())[0]))
    print("Chaves originais:", list(estado['dados_coletados'].keys()))

    # Simula serialização JSON (como acontece no banco)
    estado_json = json.dumps(estado)
    estado_recuperado = json.loads(estado_json)

    print("\nEstado recuperado (tipo de chaves):", type(list(estado_recuperado['dados_coletados'].keys())[0]))
    print("Chaves recuperadas:", list(estado_recuperado['dados_coletados'].keys()))

    # Preenche todas as etapas
    for i in range(5):
        # Usa chaves string (como vêm do JSON)
        estado_recuperado['dados_coletados'][str(i)] = f"Descrição da etapa {i+1}"

    estado_recuperado['etapa_atual'] = 5
    estado_recuperado['concluido'] = True

    print("\nEstado completo (antes de finalizar):")
    print("- Etapa atual:", estado_recuperado['etapa_atual'])
    print("- Dados coletados:", estado_recuperado['dados_coletados'])

    # Tenta criar resposta de finalização
    try:
        resultado = helena._criar_resposta_finalizacao(estado_recuperado)
        print("\n✅ SUCESSO! Resposta de finalização criada:")
        print("- Progresso:", resultado.get('progresso'))
        print("- Sugerir contexto:", resultado.get('sugerir_contexto'))
        print("- Resposta (primeiros 200 chars):", resultado['resposta'][:200])
    except Exception as e:
        print(f"\n❌ ERRO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_json_serialization()
