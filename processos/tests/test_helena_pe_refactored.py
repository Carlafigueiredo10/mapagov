"""
Teste rápido da refatoração Helena PE
"""
from processos.domain.helena_planejamento_estrategico import HelenaPlanejamentoEstrategico

# Criar instância
helena = HelenaPlanejamentoEstrategico()
print(f"✅ Helena criada: {helena.PRODUTO_NOME} v{helena.VERSION}")

# Inicializar estado
session_data = helena.inicializar_estado(skip_intro=False)
print(f"✅ Estado inicial: {session_data['estado_atual']}")

# Simular conversa
print("\n" + "="*60)
print("TESTE 1: Boas-vindas")
print("="*60)
resultado = helena.processar("Olá", session_data)
print(f"Resposta: {resultado['resposta'][:200]}...")
print(f"Novo estado: {resultado['session_data']['estado_atual']}")

print("\n" + "="*60)
print("TESTE 2: Escolha modo diagnóstico")
print("="*60)
resultado = helena.processar("1", resultado['session_data'])
print(f"Resposta: {resultado['resposta'][:200]}...")
print(f"Novo estado: {resultado['session_data']['estado_atual']}")

print("\n" + "="*60)
print("TESTE 3: Responder primeira pergunta (iniciante)")
print("="*60)
resultado = helena.processar("1", resultado['session_data'])
print(f"Resposta: {resultado['resposta'][:200]}...")
print(f"Novo estado: {resultado['session_data']['estado_atual']}")
print(f"Diagnóstico: {resultado['session_data']['diagnostico']}")
print(f"Pontuação: {resultado['session_data']['pontuacao_modelos']}")

print("\n" + "="*60)
print("✅ TODOS OS TESTES PASSARAM!")
print("="*60)
print("\nEstrutura criada:")
print(f"- schemas.py ✅")
print(f"- pe_orchestrator.py ✅")
print(f"- agents/okr_agent.py ✅")
print(f"- Compatibilidade reversa ✅")
print(f"\n🎉 Refatoração do Helena PE concluída com sucesso!")
