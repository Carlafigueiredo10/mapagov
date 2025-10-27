# ✅ FIX COMPLETO: Loop Infinito no Cenário 2+

**Data:** 2025-10-20
**Problema:** Após completar subetapas do Cenário 1, o sistema entrava em loop infinito ao pedir subetapas do Cenário 2 (e seguintes)

---

## 🐛 Problema Identificado

### Sintoma
```
✅ Cenário 1 (1.1.1) completo com subetapas:
   - 1.1.1.1 Primeira subetapa
   - 1.1.1.2 Segunda subetapa

Avançando para Cenário 2 (1.1.2)...

👤 Descreva as subetapas do Cenário 2 (1.1.2)...
[Usuário digita: 1.1.2.1 e 1.1.2.2]

👤 Descreva as subetapas do Cenário 2 (1.1.2)...  ← LOOP!
[Sistema ignora a entrada anterior]

👤 Descreva as subetapas do Cenário 2 (1.1.2)...  ← LOOP!
```

### Logs do Problema
```
[DEBUG-RESTORE] descricao=ABRIR  O SISTEMA
[DEBUG-RESTORE] operador=Técnico Especializado
[DEBUG-RESTORE] tem_condicionais=True
[DEBUG-RESTORE] tipo_condicional=binario

❌ NÃO APARECE:
   - cenarios
   - _cenario_index
```

### Causa Raiz

A **StateMachine usa `_cenario_index`** (campo privado) para rastrear qual cenário está sendo detalhado:
- `_cenario_index = 0` → Detalhando Cenário 1
- `_cenario_index = 1` → Detalhando Cenário 2
- `_cenario_index = 2` → Detalhando Cenário 3

**Mas este campo NÃO estava sendo salvo na sessão!**

Consequência:
1. Usuário completa Cenário 1 → `_cenario_index` avança para 1
2. Sessão é salva → `_cenario_index` **não é serializado**
3. Nova requisição → StateMachine restaurada → `_cenario_index` default = 0
4. Sistema pensa que ainda está detalhando Cenário 1 (index 0)
5. Loop infinito!

---

## ✅ Solução Implementada

### 1. Serializar `_cenario_index` (state_machine.py linha 133)

**Arquivo:** `processos/helena_produtos/domain/state_machine.py`

```python
def obter_estado_interno(self) -> Dict[str, Any]:
    """
    Serializa estado interno da StateMachine SEM valores default.
    Usado para salvar/restaurar estado entre requisições.
    """
    return {
        'numero': self.numero,
        'descricao': self.descricao,
        'operador': self.operador,
        'tem_condicionais': self.tem_condicionais,
        'tipo_condicional': self.tipo_condicional,
        'antes_decisao': self.antes_decisao,
        'detalhes': self.detalhes,
        'cenarios': [
            {
                'numero': c.numero,
                'descricao': c.descricao,
                'subetapas': [
                    {'numero': s.numero, 'descricao': s.descricao}
                    for s in c.subetapas
                ]
            }
            for c in self.cenarios
        ] if self.cenarios else [],
        '_cenario_index': self._cenario_index  # ✅ FIX: Salvar índice do cenário atual
    }
```

**O que faz:**
- Adiciona `_cenario_index` ao dicionário serializado
- Preserva o valor exato (0, 1, 2, etc.)
- Permite restauração precisa do estado

---

### 2. Restaurar `_cenario_index` (views.py linhas 179-182)

**Arquivo:** `processos/views.py`

```python
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

# ✅ FIX CENÁRIO LOOP: Restaurar índice do cenário sendo detalhado
if '_cenario_index' in _etapa_sm_state:
    helena._etapa_sm._cenario_index = _etapa_sm_state.get('_cenario_index', 0)
    print(f"[DEBUG-RESTORE] _cenario_index restaurado: {helena._etapa_sm._cenario_index}")
```

**O que faz:**
- Lê `_cenario_index` do estado salvo
- Restaura no objeto StateMachine
- Adiciona log de debug para verificação
- Default para 0 se não existir (retrocompatibilidade)

---

## 🔄 Fluxo Corrigido

### Antes (com bug):
```
1. Usuário completa Cenário 1 → _cenario_index = 1
2. Sessão salva (SEM _cenario_index) ❌
3. Nova requisição → StateMachine restaurada → _cenario_index default = 0
4. Sistema pensa que está no Cenário 1 (index 0)
5. Pergunta subetapas do Cenário 1 novamente
6. LOOP infinito
```

### Depois (corrigido):
```
1. Usuário completa Cenário 1 → _cenario_index = 1
2. Sessão salva (COM _cenario_index=1) ✅
3. Nova requisição → StateMachine restaurada → _cenario_index = 1 (do estado salvo)
4. Sistema sabe que está no Cenário 2 (index 1)
5. Pergunta subetapas do Cenário 2 corretamente
6. ✅ Continua fluxo normal
```

---

## 📝 Arquivos Modificados

### 1. processos/helena_produtos/domain/state_machine.py
- **Linha 133:** Adicionado `'_cenario_index': self._cenario_index`
- **Método:** `obter_estado_interno()`
- **Total:** +1 linha

### 2. processos/views.py
- **Linhas 179-182:** Adicionado bloco de restauração de `_cenario_index`
- **Seção:** Restauração de StateMachine
- **Total:** +4 linhas

---

## ✅ Como Testar

### Pré-requisitos
1. Servidor Django rodando: `python manage.py runserver 8000`
2. Frontend React rodando: `cd frontend && npm run dev` (porta 5173)
3. Navegador em http://localhost:5173

### Passos de Teste

1. **Iniciar mapeamento completo:**
   - Nome: "Teste Cenário Loop"
   - Confirmar nome (Sim)
   - Área: CGBEN (opção 1)
   - Preencher arquitetura, sistemas, normas, operadores, etc.

2. **Chegar nas etapas:**
   - Descrever etapa 1: "Abrir o sistema"
   - Operador: "Técnico Especializado"
   - Tem condicionais? **Sim**
   - Tipo: **Binário (2 cenários)**

3. **Antes da decisão:**
   - Digite: "Verificar credenciais do usuário"

4. **Descrever cenários:**
   - Sistema pedirá descrições JSON
   - Digite:
     ```json
     {"cenarios": [
       {"descricao": "Credenciais válidas"},
       {"descricao": "Credenciais inválidas"}
     ]}
     ```

5. **Detalhar Cenário 1 (1.1.1) - Credenciais válidas:**
   - Digite subetapas:
     ```
     Permitir acesso ao sistema
     Registrar login no log
     ```
   - Clicar "Confirmar e Continuar"

6. **Testar Cenário 2 (1.1.2) - Credenciais inválidas:**
   - Sistema deve perguntar: "Descreva as subetapas do Cenário 2 (1.1.2)..."
   - Digite subetapas:
     ```
     Bloquear acesso
     Enviar alerta de segurança
     ```
   - Clicar "Confirmar e Continuar"

7. **Resultado Esperado:**
   - ✅ Sistema aceita as subetapas do Cenário 2
   - ✅ NÃO repete a pergunta
   - ✅ Avança para próxima etapa ou finaliza

8. **Resultado ERRADO (se bug ainda existir):**
   - ❌ Sistema ignora as subetapas
   - ❌ Pergunta novamente "Descreva as subetapas do Cenário 2..."
   - ❌ Loop infinito

### Verificar Logs

Abra terminal do Django e procure por:
```
[DEBUG-RESTORE] _cenario_index restaurado: 1  ← Deve aparecer quando detalhar Cenário 2
```

---

## 🎯 Impacto

### Positivo
- ✅ Fix completo do loop infinito em cenários
- ✅ Suporta etapas condicionais com múltiplos cenários (2, 3, 4+)
- ✅ Preserva progresso do usuário entre requisições
- ✅ Permite mapear processos complexos com decisões

### Retrocompatibilidade
- ✅ Default para 0 se `_cenario_index` não existir (sessões antigas)
- ✅ Não quebra POPs sem condicionais (etapas lineares)
- ✅ Compatível com serialização anterior

### Performance
- ⚠️ Adiciona 1 campo ao estado da sessão (~4 bytes)
- ⚠️ Impacto desprezível (total do estado ~500 bytes)

---

## 🐛 Edge Cases Tratados

1. **Cenário único:** Se só tem 1 cenário, `_cenario_index` sempre será 0 (funciona)
2. **Sem cenários:** Se etapa é linear, `_cenario_index` não é usado (ignorado)
3. **Cenários sem subetapas:** Se usuário pular subetapas, index avança normalmente
4. **Múltiplos cenários:** Funciona para 2, 3, 4+ cenários

---

## 📚 Referências

- **StateMachine pattern:** `processos/helena_produtos/domain/state_machine.py`
- **Handler de subetapas:** `state_machine.py::_processar_subetapas_cenario()` (linhas 210-237)
- **Serialização:** `state_machine.py::obter_estado_interno()` (linhas 105-134)
- **Restauração:** `processos/views.py` (linhas 138-202)

---

## 📊 Histórico de Bugs Relacionados

1. ✅ **Bug #1 - Loop Operador:** Operador não avançava para pergunta de condicionais
   - **Fix:** Reordenar IFs no adapter (priorizar "pergunta" sobre "proximo")
   - **Arquivo:** `processos/helena_produtos/app/adapters.py`

2. ✅ **Bug #2 - "Não especificado":** Valores default quebravam detecção de estado
   - **Fix:** Criar `obter_estado_interno()` separado de `obter_dict()`
   - **Arquivo:** `processos/helena_produtos/domain/state_machine.py`

3. ✅ **Bug #3 - Loop Cenário (ESTE FIX):** `_cenario_index` não persistia
   - **Fix:** Adicionar `_cenario_index` à serialização e restauração
   - **Arquivos:** `state_machine.py` + `views.py`

---

**Status:** ✅ **IMPLEMENTADO - PRONTO PARA TESTE**

**Próximo passo:** Usuário testar no navegador seguindo os passos acima e confirmar que o loop foi eliminado.
