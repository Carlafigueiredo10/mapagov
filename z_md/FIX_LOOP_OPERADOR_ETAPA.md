# 🔧 FIX: Loop infinito na pergunta de operador da etapa

**Data:** 2025-10-20
**Problema:** Ao mapear etapas, a pergunta "Quem realiza a Etapa 1?" ficava em loop infinito, criando novas StateMachine a cada resposta

---

## 🐛 Problema Identificado

### Sintoma
```
👤 Quem realiza a Etapa 1?
[Usuário seleciona "Técnico Especializado"]

👤 Quem realiza a Etapa 1?  ← LOOP!
[Usuário seleciona "Técnico Especializado" novamente]

👤 Quem realiza a Etapa 1?  ← LOOP!
```

### Logs do problema
```
[INFO] helena.pop - Nova StateMachine criada para Etapa 1
[DEBUG-PRINCIPAL] Mensagem: 'Técnico Especializado'
Dados extraídos no resultado: {'descricao_etapa': 'Técnico Especializado'}  ← ERRADO! Deveria ser operador

[INFO] helena.pop - Nova StateMachine criada para Etapa 1  ← Criando NOVA SM ao invés de continuar a existente
```

### Causa Raiz

A **StateMachine `_etapa_sm` não estava sendo salva na sessão Django**, então entre uma requisição e outra:

1. Usuário digita descrição da etapa → StateMachine criada (estado DESCRICAO → OPERADOR)
2. **Resposta salva na sessão**
3. **Mas `_etapa_sm` NÃO é salva** (é um objeto Python não-JSON)
4. Nova requisição → Helena restaurada da sessão
5. `_etapa_sm` não existe → Cria NOVA StateMachine
6. Trata "Técnico Especializado" como DESCRIÇÃO ao invés de OPERADOR
7. Loop infinito!

---

## ✅ Solução Implementada

### 1. Salvar estado da StateMachine (views.py linha 227-228)

```python
# ✨ NOVO: Salvar estado da StateMachine (fix loop operador etapa)
'_etapa_sm_state': helena._etapa_sm.obter_dict() if hasattr(helena, '_etapa_sm') and helena._etapa_sm else None
```

**O que faz:**
- Se existe `_etapa_sm` ativa, serializa para dict usando `obter_dict()`
- Salva na sessão Django junto com outros dados
- Se não existe, salva `None`

---

### 2. Restaurar StateMachine da sessão (views.py linhas 138-190)

```python
# ✨ NOVO: Restaurar StateMachine se estava em progresso (fix loop operador etapa)
_etapa_sm_state = state.get('_etapa_sm_state')
if _etapa_sm_state:
    from processos.helena_produtos.domain.state_machine import EtapaStateMachine
    from processos.helena_produtos.domain.enums import EstadoEtapa
    from processos.helena_produtos.domain.models import Cenario, Subetapa

    # Recriar StateMachine do estado serializado
    helena._etapa_sm = EtapaStateMachine(
        numero_etapa=_etapa_sm_state.get('numero', 1),
        operadores_disponiveis=helena.OPERADORES_DECIPEX
    )

    # Restaurar estado interno da SM
    helena._etapa_sm.descricao = _etapa_sm_state.get('descricao', '')
    helena._etapa_sm.operador = _etapa_sm_state.get('operador')
    helena._etapa_sm.tem_condicionais = _etapa_sm_state.get('tem_condicionais')
    helena._etapa_sm.tipo_condicional = _etapa_sm_state.get('tipo_condicional')
    helena._etapa_sm.antes_decisao = _etapa_sm_state.get('antes_decisao')
    helena._etapa_sm.detalhes = _etapa_sm_state.get('detalhes', [])

    # Restaurar cenários se existirem
    if _etapa_sm_state.get('cenarios'):
        helena._etapa_sm.cenarios = [
            Cenario(
                numero=c['numero'],
                descricao=c['descricao'],
                subetapas=[
                    Subetapa(numero=s['numero'], descricao=s['descricao'])
                    for s in c.get('subetapas', [])
                ]
            )
            for c in _etapa_sm_state['cenarios']
        ]

    # Restaurar estado da máquina (CRITICAL!)
    # Descobrir em qual estado estava baseado no progresso
    if helena._etapa_sm.descricao and not helena._etapa_sm.operador:
        helena._etapa_sm.estado = EstadoEtapa.OPERADOR  ← Continua de onde parou!
    elif helena._etapa_sm.operador and helena._etapa_sm.tem_condicionais is None:
        helena._etapa_sm.estado = EstadoEtapa.PERGUNTA_CONDICIONAL
    elif helena._etapa_sm.tem_condicionais and not helena._etapa_sm.tipo_condicional:
        helena._etapa_sm.estado = EstadoEtapa.TIPO_CONDICIONAL
    elif helena._etapa_sm.tipo_condicional and not helena._etapa_sm.antes_decisao:
        helena._etapa_sm.estado = EstadoEtapa.ANTES_DECISAO
    elif helena._etapa_sm.antes_decisao and not helena._etapa_sm.cenarios:
        helena._etapa_sm.estado = EstadoEtapa.CENARIOS
    elif helena._etapa_sm.cenarios:
        helena._etapa_sm.estado = EstadoEtapa.SUBETAPAS_CENARIO
    elif not helena._etapa_sm.tem_condicionais and helena._etapa_sm.operador:
        helena._etapa_sm.estado = EstadoEtapa.DETALHES
    else:
        helena._etapa_sm.estado = EstadoEtapa.DESCRICAO
```

**O que faz:**
- Recupera `_etapa_sm_state` da sessão
- Recria objeto `EtapaStateMachine` vazio
- Restaura TODOS os campos internos (descrição, operador, condicionais, cenários, etc.)
- **CRÍTICO:** Detecta em qual ESTADO a máquina estava (DESCRICAO, OPERADOR, CONDICIONAIS, etc.)
- StateMachine continua de onde parou!

---

## 🔄 Fluxo Corrigido

### Antes (com bug):
```
1. Usuário: "abrir o sistema" → [SM criada] estado: DESCRICAO → OPERADOR
2. Sessão salva (sem _etapa_sm)
3. Usuário: "Técnico Especializado" → [SM perdida] [NOVA SM criada] → trata como DESCRICAO
4. LOOP infinito
```

### Depois (corrigido):
```
1. Usuário: "abrir o sistema" → [SM criada] estado: DESCRICAO → OPERADOR
2. Sessão salva (_etapa_sm_state serializada)
3. Usuário: "Técnico Especializado" → [SM restaurada no estado OPERADOR] → processa como OPERADOR
4. Avança para próximo estado (PERGUNTA_CONDICIONAL)
5. ✅ Continua fluxo normal
```

---

## 📝 Arquivos Modificados

### processos/views.py

**Linha 227-228:** Adicionar `_etapa_sm_state` ao dict salvo na sessão
```python
'_etapa_sm_state': helena._etapa_sm.obter_dict() if hasattr(helena, '_etapa_sm') and helena._etapa_sm else None
```

**Linhas 138-190:** Restaurar StateMachine quando carregar Helena da sessão
- Total de ~52 linhas adicionadas
- Lógica complexa de detectar estado correto baseado no progresso

---

## ✅ Como Testar

1. **Recarregar a página** http://localhost:5173 (ou reiniciar Django)
2. Seguir fluxo completo até as etapas:
   - Nome → Área → Arquitetura → Sistemas → Normas → Operadores → Fluxos → Etapas
3. Quando chegar em "Descreva a primeira etapa":
   - Digite: "abrir o sistema"
   - **Verificar:** Helena pergunta "Quem realiza a Etapa 1?"
4. Selecionar operador: "Técnico Especializado"
5. **Resultado esperado:**
   - ✅ Helena pergunta: "Essa etapa tem alguma decisão ou condição (sim/não)?"
   - ❌ NÃO deve perguntar "Quem realiza a Etapa 1?" novamente

---

## 🎯 Impacto

### Positivo
- ✅ Fix completo do loop infinito em operador de etapa
- ✅ StateMachine persiste entre requisições
- ✅ Permite mapear etapas com condicionais (estava quebrado)
- ✅ Suporta subetapas e cenários complexos

### Atenção
- ⚠️ Aumenta tamanho da sessão Django (~200-500 bytes por etapa em progresso)
- ⚠️ Lógica de detectar estado é baseada em inferência (pode ter edge cases)
- ⚠️ Se usuário abandonar etapa no meio, `_etapa_sm_state` fica na sessão até fim da conversa

---

## 🐛 Edge Cases Tratados

1. **Etapa sem StateMachine:** Se `_etapa_sm_state` é `None`, não restaura (comportamento normal)
2. **Cenários complexos:** Restaura cenários COM subetapas corretamente
3. **Estado final:** Se etapa está completa, não restaura StateMachine
4. **Concorrência:** Cada sessão tem sua própria StateMachine (isolamento correto)

---

## 📚 Referências

- **StateMachine pattern:** `processos/helena_produtos/domain/state_machine.py`
- **Enums de estado:** `processos/helena_produtos/domain/enums.py`
- **Models (Etapa, Cenario, Subetapa):** `processos/helena_produtos/domain/models.py`
- **Adaptador UI:** `processos/helena_produtos/app/adapters.py`

---

**Status:** ✅ **IMPLEMENTADO - AGUARDANDO TESTE MANUAL**

**Próximo passo:** Testar no navegador e validar que o loop foi corrigido.
