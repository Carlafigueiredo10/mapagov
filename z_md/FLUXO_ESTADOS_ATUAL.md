# FLUXO DE ESTADOS DO HELENA POP (VERIFICAÇÃO COMPLETA)

## 1. INÍCIO → NOME E EXPLICAÇÃO
```
NOME_USUARIO
  ↓ (confirma)
CONFIRMA_NOME
  ↓ (sim)
ESCOLHA_TIPO_EXPLICACAO
  ↓ (longa)
EXPLICACAO_LONGA
  ↓
EXPLICACAO
  ↓
PEDIDO_COMPROMISSO
  ↓
AREA_DECIPEX
```

## 2. ÁREA E ARQUITETURA
```
AREA_DECIPEX
  ↓ (se tem subárea)
SUBAREA_DECIPEX
  ↓ (ou direto)
ARQUITETURA
  ↓
CONFIRMACAO_ARQUITETURA
  ↓ (confirma)
NOME_PROCESSO (=ENTREGA_ESPERADA)
```

## 3. COLETA DE DADOS (ORDEM NOVA - PÓS FIX)
```
ENTREGA_ESPERADA
  ↓
CONFIRMACAO_ENTREGA
  ↓
RECONHECIMENTO_ENTREGA (badge)
  ↓
SISTEMAS ← NOVO: Vem logo após entrega!
  ↓
DISPOSITIVOS_NORMATIVOS (normas)
  ↓
OPERADORES
  ↓
FLUXOS (entrada + saída)
  ↓
PONTOS_ATENCAO
```

## 4. REVISÃO E FINALIZAÇÃO
```
PONTOS_ATENCAO
  ↓
REVISAO_PRE_DELEGACAO
  ↓ (tudo certo)
TRANSICAO_EPICA
  ↓
DELEGACAO_ETAPAS
  ↓
FINALIZADO
```

## 5. INTERFACES QUE DEVEM SER MOSTRADAS

| Estado | Interface | Handler |
|--------|-----------|---------|
| AREA_DECIPEX | `areas` | `_processar_area_decipex` |
| SUBAREA_DECIPEX | `subareas` | `_processar_subarea_decipex` |
| ARQUITETURA | `dropdown_*` | `_processar_arquitetura` |
| CONFIRMACAO_ARQUITETURA | `confirmacao_arquitetura` | `_processar_confirmacao_arquitetura` |
| ENTREGA_ESPERADA | texto livre | `_processar_entrega_esperada` |
| SISTEMAS | `sistemas` | `_processar_sistemas` |
| DISPOSITIVOS_NORMATIVOS | `normas` | `_processar_dispositivos_normativos` |
| OPERADORES | `operadores` | `_processar_operadores` |
| FLUXOS | `entrada_processo` | `_processar_fluxos` |
| PONTOS_ATENCAO | texto livre | `_processar_pontos_atencao` |
| REVISAO_PRE_DELEGACAO | `revisao` | `_processar_revisao_pre_delegacao` |
| TRANSICAO_EPICA | `transicao_epica` | `_processar_transicao_epica` |

## 6. VERIFICAR PROBLEMAS

### ✅ SISTEMAS - FUNCIONANDO
- Transição: RECONHECIMENTO_ENTREGA → SISTEMAS (linha 2428)
- Interface: configurada em `processar()` linhas 1437-1444
- Frontend: `InterfaceSistemas.tsx` envia `JSON.stringify([...])`
- Backend: parse JSON em `_processar_sistemas` linha 2549

### ❌ OPERADORES - ERA O PROBLEMA (CORRIGIDO)
- Transição: DISPOSITIVOS_NORMATIVOS → OPERADORES (linha 2478)
- Interface: configurada em `processar()` linhas 1428-1435
- Frontend: `InterfaceOperadores.tsx` estava enviando string com vírgulas
- **FIX**: Mudado para enviar `JSON.stringify([...])`
- Backend: parse JSON em `_processar_operadores` linha 2501

### ? FLUXOS - VERIFICAR
- Transição: OPERADORES → FLUXOS (linha 2511)
- Interface: configurada em `_processar_operadores` linhas 2514-2533
- Frontend: `InterfaceEntradaProcesso.tsx` envia string com `|`
- Backend: parse com `split('|')` linha 2600
- **STATUS**: Parece OK, mas precisa testar

## 7. FORMATOS DE DADOS ESPERADOS PELO BACKEND

| Campo | Frontend Envia | Backend Espera |
|-------|---------------|----------------|
| Sistemas | `JSON.stringify(["SIAPE", "SEI"])` | JSON array ou 'nenhum' |
| Normas | `JSON.stringify([...])` | JSON array ou texto |
| Operadores | `JSON.stringify(["EXECUTOR"])` ✅ FIX | JSON array ou texto |
| Fluxos Entrada | `"item1 | item2 | item3"` | String com `|` |
| Fluxos Saída | texto livre | String com vírgulas |

