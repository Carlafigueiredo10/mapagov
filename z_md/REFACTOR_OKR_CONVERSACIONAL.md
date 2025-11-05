# Refatoração OKR Agent - Modo Conversacional Natural

## Problema Atual
O agente ainda segue etapas fixas:
1. Pergunta trimestre (técnico demais)
2. Pergunta objetivo
3. Pergunta KRs

Isso quebra o paradigma de "mentora estratégica" - a Helena deve conversar naturalmente.

## Nova Abordagem

### Fluxo Natural:
1. **Início**: "O que você gostaria de ver melhorando?"
2. **Escuta ativa**: Interpreta resposta do usuário
3. **Tradução**: Converte para objetivo formal
4. **Contextual**: Só pergunta horizonte de tempo se fizer sentido
5. **Colaborativa**: Sugere KRs baseado no contexto

### Mudanças Necessárias:

#### 1. Eliminar verificação de `trimestre` no fluxo
```python
# ANTES
if not estrutura_atual.get('trimestre'):
    # Pergunta trimestre...

# DEPOIS
# Nenhuma verificação de trimestre
# Helena vai direto para entender o objetivo
```

#### 2. Tornar pergunta de horizonte contextual
```python
# Só pergunta após entender o objetivo e KRs
# Exemplo: "Esses resultados são para os próximos 3 meses, 6 meses ou o ano todo?"
```

#### 3. Remover linguagem de "etapas"
```python
# ANTES: "ETAPA 1: Definir trimestre"
# DEPOIS: Conversa fluida sem mencionar etapas
```

## Implementação
- Reescrever `processar_mensagem()` para modo conversacional
- Eliminar checagem de `trimestre`
- Tornar horizonte de tempo opcional e contextual
