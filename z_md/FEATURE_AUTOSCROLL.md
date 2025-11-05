# ✨ FEATURE - Auto-Scroll Progressivo

**Data**: 2025-11-01
**Status**: IMPLEMENTADO

---

## 🎯 OBJETIVO

Fazer a tela rolar automaticamente conforme as partes da mensagem vão aparecendo, criando uma experiência mais fluida e natural.

---

## 💡 COMPORTAMENTO

### Antes:
- ✅ Mensagem aparece em partes com delays
- ❌ Usuário precisa rolar manualmente para ver novas partes
- ❌ Partes podem ficar fora da tela

### Depois:
- ✅ Mensagem aparece em partes com delays
- ✅ Tela rola automaticamente conforme novas partes surgem
- ✅ Scroll suave (`behavior: 'smooth'`)
- ✅ Sempre mostra a parte mais recente

---

## 🔨 IMPLEMENTAÇÃO

### Arquivo: `MessageBubble.tsx`

#### 1. Adicionar useRef (linha 8 e 17)
```typescript
import { useState, useEffect, useRef } from 'react';

function MessageBubble({ message }: MessageBubbleProps) {
  const messageEndRef = useRef<HTMLDivElement>(null);
  // ...
}
```

#### 2. Adicionar useEffect de auto-scroll (linha 91-99)
```typescript
// ✅ Auto-scroll suave conforme partes vão aparecendo
useEffect(() => {
  if (partesVisiveis.length > 0 && messageEndRef.current) {
    messageEndRef.current.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest'
    });
  }
}, [partesVisiveis.length]);
```

**Lógica**:
- Monitora `partesVisiveis.length` (número de partes exibidas)
- Quando uma nova parte aparece, length aumenta
- Dispara scroll suave até a ref

#### 3. Adicionar div com ref (linha 181-182)
```tsx
{/* ✅ Ref para auto-scroll progressivo */}
<div ref={messageEndRef} style={{ height: '1px' }} />
```

**Posição**: Logo após as partes renderizadas, antes de badges/interfaces

---

## 📊 FLUXO

```
1. Mensagem chega com [DELAY:1500]
2. Primeira parte aparece (imediata)
   → partesVisiveis = [parte1]
   → useEffect detecta length = 1
   → Scroll até messageEndRef

3. Após 1500ms: Segunda parte aparece
   → partesVisiveis = [parte1, parte2]
   → useEffect detecta length = 2
   → Scroll suave até messageEndRef

4. Após mais 1500ms: Terceira parte aparece
   → partesVisiveis = [parte1, parte2, parte3]
   → useEffect detecta length = 3
   → Scroll suave até messageEndRef

... e assim por diante
```

---

## ⚙️ PARÂMETROS DO SCROLL

### `scrollIntoView` options:

```typescript
{
  behavior: 'smooth',  // Animação suave (não instantânea)
  block: 'nearest'     // Rola apenas o necessário
}
```

**Alternativas**:
- `block: 'start'` - Alinha no topo
- `block: 'end'` - Alinha no final
- `block: 'center'` - Centraliza
- `block: 'nearest'` - Rola o mínimo possível ← **ESCOLHIDO**

**Motivo**: `nearest` evita scroll excessivo se a parte já estiver visível.

---

## 🎬 EXEMPLO VISUAL

### Timeline de scroll:
```
[0ms]    Parte 1 aparece
         ↓ scroll suave
         Parte 1 visível

[1500ms] Parte 2 aparece
         ↓ scroll suave
         Partes 1-2 visíveis

[3000ms] Parte 3 aparece
         ↓ scroll suave
         Partes 1-3 visíveis

[4500ms] Parte 4 aparece
         ↓ scroll suave
         Partes 1-4 visíveis
```

---

## 🧪 TESTES

### Casos a validar:
- [x] Scroll acontece ao adicionar nova parte
- [x] Scroll é suave (não instantâneo)
- [ ] Não interfere com scroll manual do usuário
- [ ] Funciona em diferentes tamanhos de tela
- [ ] Não causa scroll infinito (loop)

### Como testar:
1. Acessar Helena POP
2. Escolher "explicação detalhada"
3. Observar:
   - ✅ Tela rola automaticamente
   - ✅ Sempre mostra a parte mais recente
   - ✅ Scroll é suave

---

## 📝 ARQUIVOS MODIFICADOS

| Arquivo | Linhas | Mudança |
|---------|--------|---------|
| `MessageBubble.tsx` | 8 | Import `useRef` |
| `MessageBubble.tsx` | 17 | Declaração `messageEndRef` |
| `MessageBubble.tsx` | 91-99 | useEffect de auto-scroll |
| `MessageBubble.tsx` | 181-182 | Div com ref (invisível) |

---

## 🎨 MELHORIAS FUTURAS (OPCIONAIS)

### 1. Detectar scroll manual do usuário
```typescript
const [userScrolled, setUserScrolled] = useState(false);

// Pausar auto-scroll se usuário rolou manualmente
useEffect(() => {
  const handleScroll = () => setUserScrolled(true);
  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll);
}, []);

// Auto-scroll apenas se usuário não rolou
if (!userScrolled && partesVisiveis.length > 0) {
  messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
}
```

### 2. Scroll apenas para mensagens da Helena
```typescript
if (message.tipo === 'helena' && partesVisiveis.length > 0) {
  // auto-scroll apenas para mensagens da Helena
}
```

### 3. Delay entre scroll e aparição
```typescript
setTimeout(() => {
  messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
}, 100); // pequeno delay para animação render
```

---

## 🔙 REVERSÃO (se necessário)

### Remover auto-scroll:
```typescript
// Comentar useEffect de auto-scroll
// Remover ref do JSX
// Remover import useRef
```

---

## ✅ STATUS FINAL

- ✅ Auto-scroll implementado
- ✅ Scroll suave funcionando
- ✅ Ref invisível adicionada
- ✅ Comportamento natural

**PRONTO PARA TESTES!**
