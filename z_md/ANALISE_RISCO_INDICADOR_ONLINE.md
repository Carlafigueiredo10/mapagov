# 🔍 ANÁLISE DE RISCO - Indicador Online/Offline no Header

**Data**: 2025-11-01
**Solicitação**: Adicionar indicador "online" no header quando backend estiver ativo
**Localização**: [ChatContainer.tsx:226](frontend/src/components/Helena/ChatContainer.tsx#L226)

---

## 📋 SUMÁRIO EXECUTIVO

### ✅ Viabilidade: **MÉDIA-ALTA**
### ⚠️ Risco Geral: **MÉDIO**
### 💰 Custo de Implementação: **BAIXO**
### 🎯 Impacto UX: **POSITIVO**

**Recomendação**: **IMPLEMENTAR com mitigações de risco**

---

## 🎯 OBJETIVO

Adicionar um indicador visual no header da aplicação que mostre:
- ✅ **"Online"** (verde) quando backend está respondendo
- ❌ **"Offline"** (vermelho) quando backend não responde

```
┌─────────────────────────────────────────────┐
│ Helena - Assistente DECIPEX    ● Online    │  ← NOVO
│ Mapeamento conversacional de POPs          │
└─────────────────────────────────────────────┘
```

---

## ⚠️ ANÁLISE DE RISCOS

### 🔴 RISCOS CRÍTICOS

#### 1. **Falso Positivo de "Offline"**
**Probabilidade**: ALTA | **Impacto**: ALTO

**Descrição**:
- Backend pode estar online mas demorar >2min para responder (timeout atual: 120s)
- Processamento de RAG/IA pode levar 30-60s
- Indicador pode mostrar "offline" enquanto backend está processando

**Cenário Real**:
```typescript
// useChat.ts linha 104-117
if (isDescricaoInicial) {
  // Quadro roxo: processamento pode levar 30-60s
  // Se health check rodar a cada 10s, vai mostrar "offline" incorretamente
}
```

**Impacto no Usuário**:
- 😰 Usuário acha que perdeu conexão
- 🔄 Usuário recarrega página (perde progresso)
- 📞 Usuário abre chamado de suporte (falso alarme)

**Mitigação**:
- ✅ Não verificar saúde durante `isProcessing === true`
- ✅ Aumentar timeout do health check (não confundir com timeout de chat)
- ✅ Mostrar "Processando..." ao invés de "Offline" durante chat ativo

---

#### 2. **Overhead de Requisições**
**Probabilidade**: MÉDIA | **Impacto**: MÉDIO

**Descrição**:
- Health check a cada 10s = 360 requisições/hora por usuário
- 100 usuários simultâneos = 36.000 requisições/hora
- Pode sobrecarregar backend Django (especialmente se usar banco de dados)

**Impacto**:
```
Django Backend (Gunicorn 4 workers)
├─ 36.000 health checks/hora
├─ + Requisições normais de chat
└─> Risco de saturação em horário de pico
```

**Mitigação**:
- ✅ Endpoint `/health/` levíssimo (sem DB, só retorna 200)
- ✅ Health check a cada 30s (não 10s)
- ✅ Parar health check quando usuário inativo (sem interação por 5min)
- ✅ Usar `HEAD` ao invés de `GET` (menos bytes trafegados)

---

### 🟡 RISCOS MÉDIOS

#### 3. **Conflito com Sistema de Erro do Axios**
**Probabilidade**: MÉDIA | **Impacto**: MÉDIO

**Descrição**:
- Axios já tem interceptor de erro ([api.ts:30-49](frontend/src/services/api.ts#L30-L49))
- Health check falhado dispara interceptor e loga erro no console
- Usuário vê console cheio de erros vermelhos (mesmo comportamento esperado)

**Exemplo**:
```typescript
// api.ts linha 43-44
if (error.message === 'Network Error') {
  console.error('❌ Erro de rede. Verifique se o backend está rodando.');
  // ^ Isso vai disparar a cada health check falhado
}
```

**Mitigação**:
- ✅ Health check deve usar instância Axios separada (sem interceptors)
- ✅ Ou adicionar flag `skipInterceptor` no config

---

#### 4. **Assincronicidade entre Estado e Realidade**
**Probabilidade**: MÉDIA | **Impacto**: BAIXO

**Descrição**:
- Backend pode cair 1s depois do health check passar
- Indicador mostra "online" mas próxima requisição falha
- Janela de 10-30s entre checks cria lag de informação

**Cenário**:
```
10:00:00 - Health check: ✅ Online
10:00:15 - Backend crashea 💥
10:00:20 - Usuário envia mensagem ❌ Falha
10:00:30 - Health check: ❌ Offline (15s depois do crash)
```

**Mitigação**:
- ✅ Adicionar detecção de erro em requisições reais (fallback)
- ✅ Atualizar indicador imediatamente se chat falhar
- ✅ Health check é apenas hint visual, não garantia

---

### 🟢 RISCOS BAIXOS

#### 5. **Impacto Visual/UX**
**Probabilidade**: BAIXA | **Impacto**: BAIXO

**Descrição**:
- Indicador pode ficar "piscando" se conexão instável
- Pode distrair usuário durante conversa
- Ocupa espaço no header (já está apertado)

**Mitigação**:
- ✅ Debounce de 5s antes de mudar estado (evita piscar)
- ✅ Transição suave CSS (fade 0.3s)
- ✅ Tamanho pequeno: 8px dot + texto "Online" (60px total)

---

## 🛠️ PROPOSTAS DE IMPLEMENTAÇÃO

### 📌 OPÇÃO 1: Health Check Simples (RECOMENDADO)

**Complexidade**: Baixa
**Risco**: Médio
**Benefício**: Alto

```typescript
// frontend/src/hooks/useBackendHealth.ts
import { useState, useEffect } from 'react';
import axios from 'axios';

const healthApi = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 5000, // 5s timeout para health check
});

export const useBackendHealth = (enabled: boolean = true) => {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [lastCheck, setLastCheck] = useState<Date>(new Date());

  useEffect(() => {
    if (!enabled) return;

    const checkHealth = async () => {
      try {
        await healthApi.head('/health/'); // Endpoint levíssimo
        setIsOnline(true);
        setLastCheck(new Date());
      } catch (error) {
        setIsOnline(false);
        setLastCheck(new Date());
      }
    };

    // Check inicial
    checkHealth();

    // Check a cada 30s
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, [enabled]);

  return { isOnline, lastCheck };
};
```

**Backend** ([processos/urls.py](processos/urls.py)):
```python
# processos/urls.py
from django.http import JsonResponse

def health_check(request):
    """Health check levíssimo - sem DB, sem lógica"""
    return JsonResponse({'status': 'ok'}, status=200)

urlpatterns = [
    path('api/health/', health_check, name='health_check'),
    # ...
]
```

**Uso** ([ChatContainer.tsx:225](frontend/src/components/Helena/ChatContainer.tsx#L225)):
```tsx
import { useBackendHealth } from '../../hooks/useBackendHealth';

const ChatContainer: React.FC<ChatContainerProps> = ({ className = '' }) => {
  const { isOnline } = useBackendHealth(!isProcessing); // Pausa durante processamento

  return (
    <div className="chat-header-pop">
      <div className="header-content">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h2>Helena - Assistente DECIPEX</h2>
          <span className={`status-indicator ${isOnline ? 'online' : 'offline'}`}>
            <span className="status-dot"></span>
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </div>
        <p>Mapeamento conversacional de POPs</p>
      </div>
    </div>
  );
};
```

**CSS** ([ChatContainer.css](frontend/src/components/Helena/ChatContainer.css)):
```css
.status-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.status-indicator.online {
  background: rgba(34, 197, 94, 0.2);
  color: #16a34a;
}

.status-indicator.offline {
  background: rgba(239, 68, 68, 0.2);
  color: #dc2626;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

---

### 📌 OPÇÃO 2: Detecção Passiva (MENOR RISCO)

**Complexidade**: Muito Baixa
**Risco**: Baixo
**Benefício**: Médio

**Descrição**: Não faz health checks ativos. Apenas detecta erros nas requisições reais.

```typescript
// useChatStore.ts
interface ChatStore {
  // ...
  backendOnline: boolean;
  setBackendOnline: (online: boolean) => void;
}

// useChat.ts
try {
  const response = await chatHelena(request);
  useChatStore.getState().setBackendOnline(true); // ✅ Backend respondeu
} catch (err) {
  useChatStore.getState().setBackendOnline(false); // ❌ Backend falhou
  throw err;
}
```

**Vantagens**:
- ✅ Zero overhead (nenhuma requisição extra)
- ✅ Reflete estado real (baseado em requisições verdadeiras)
- ✅ Implementação trivial

**Desvantagens**:
- ❌ Só atualiza quando usuário interage
- ❌ Pode ficar "offline" por 30-60s durante processamento RAG
- ❌ Primeiro uso não sabe se está online

---

### 📌 OPÇÃO 3: Híbrido (MAIS ROBUSTO)

**Complexidade**: Média
**Risco**: Baixo
**Benefício**: Muito Alto

**Descrição**: Combina health check + detecção passiva + lógica inteligente

```typescript
export const useBackendHealth = () => {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const { isProcessing } = useChatStore();
  const lastRequestTime = useRef<Date>(new Date());

  // 1. Detecção passiva (prioridade)
  useEffect(() => {
    const unsubscribe = useChatStore.subscribe((state) => {
      // Se última requisição foi sucesso, assume online
      if (state.lastRequestSuccess) {
        setIsOnline(true);
        lastRequestTime.current = new Date();
      }
    });
    return unsubscribe;
  }, []);

  // 2. Health check ativo (apenas se inativo por >60s)
  useEffect(() => {
    if (isProcessing) return; // Pausa durante processamento

    const checkHealth = async () => {
      const timeSinceLastRequest = Date.now() - lastRequestTime.current.getTime();

      // Só faz health check se passou >60s sem requisição
      if (timeSinceLastRequest < 60000) return;

      try {
        await healthApi.head('/health/');
        setIsOnline(true);
      } catch {
        setIsOnline(false);
      }
    };

    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [isProcessing]);

  return { isOnline };
};
```

**Vantagens**:
- ✅ Melhor dos dois mundos
- ✅ Overhead mínimo (health check só se inativo)
- ✅ Atualização instantânea em requisições reais
- ✅ Não mostra "offline" durante processamento

**Desvantagens**:
- ❌ Implementação mais complexa
- ❌ Precisa modificar store

---

## 📊 COMPARAÇÃO DE OPÇÕES

| Critério | Opção 1: Health Check | Opção 2: Passiva | Opção 3: Híbrido |
|----------|----------------------|------------------|------------------|
| **Complexidade** | 🟡 Média | 🟢 Baixa | 🟠 Alta |
| **Overhead** | 🟠 360 req/h/user | 🟢 0 req | 🟢 ~10 req/h/user |
| **Precisão** | 🟡 Boa (lag 30s) | 🟠 Média | 🟢 Excelente |
| **Falso Positivo** | 🟠 Risco médio | 🟢 Baixo | 🟢 Muito baixo |
| **Tempo Impl.** | 1-2h | 30min | 3-4h |
| **Manutenção** | 🟢 Simples | 🟢 Simples | 🟡 Moderada |

---

## 🎯 RECOMENDAÇÃO FINAL

### 🏆 Implementar **OPÇÃO 1** (Health Check Simples) com mitigações:

**Justificativa**:
1. ✅ Melhor custo-benefício (2h implementação, benefício UX significativo)
2. ✅ Overhead aceitável com mitigações (30s interval + pausa durante processing)
3. ✅ Não requer modificação no store (menos risco de quebrar funcionalidades existentes)
4. ✅ Fácil de desabilitar se causar problemas

**Mitigações OBRIGATÓRIAS**:
1. ✅ Health check a cada **30s** (não 10s)
2. ✅ Pausar durante `isProcessing === true`
3. ✅ Endpoint `/health/` sem acesso a DB
4. ✅ Timeout de 5s no health check
5. ✅ Usar instância Axios separada (sem interceptors)
6. ✅ Debounce de 5s antes de mostrar "offline"
7. ✅ Transição CSS suave (evitar "piscar")

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Frontend

- [ ] Criar `frontend/src/hooks/useBackendHealth.ts`
- [ ] Criar instância Axios separada para health check
- [ ] Adicionar lógica de pausa durante `isProcessing`
- [ ] Adicionar debounce de 5s
- [ ] Integrar no `ChatContainer.tsx` linha 225
- [ ] Adicionar CSS para indicador (dot + texto)
- [ ] Testar com backend offline
- [ ] Testar com backend lento (>30s)
- [ ] Testar durante processamento RAG

### Backend

- [ ] Criar endpoint `GET /api/health/` em `processos/urls.py`
- [ ] Garantir que endpoint não acessa DB
- [ ] Testar resposta <50ms
- [ ] Adicionar logs (opcional, para monitoramento)

### Testes

- [ ] Verificar overhead em 10 usuários simultâneos
- [ ] Verificar não dispara erro no console durante uso normal
- [ ] Verificar indicador não "pisca" em conexão instável
- [ ] Verificar não mostra "offline" durante quadro roxo animado

---

## 🚨 CRITÉRIOS DE ROLLBACK

Se após implementação ocorrer:

1. ❌ Backend Django fica lento (P50 latency aumenta >20%)
2. ❌ Logs cheios de erros de health check
3. ❌ Usuários reclamam de indicador "piscando"
4. ❌ Indicador mostra "offline" durante uso normal

**Ação**: Desabilitar health check (comentar `useBackendHealth(true)` → `useBackendHealth(false)`)

---

## 📈 MÉTRICAS DE SUCESSO

### Após 1 semana de produção:

- ✅ Overhead: <1% aumento no número de requisições totais
- ✅ Falsos positivos: <5% do tempo (indicador "offline" quando backend online)
- ✅ Feedback positivo: >80% usuários acham útil (survey opcional)
- ✅ Tempo de detecção: <60s entre backend cair e indicador mostrar "offline"

---

## 🔗 ARQUIVOS AFETADOS

### Novos Arquivos:
1. `frontend/src/hooks/useBackendHealth.ts` (novo)

### Arquivos Modificados:
1. [frontend/src/components/Helena/ChatContainer.tsx:225](frontend/src/components/Helena/ChatContainer.tsx#L225) - Adicionar indicador
2. [frontend/src/components/Helena/ChatContainer.css:13](frontend/src/components/Helena/ChatContainer.css#L13) - Estilos do indicador
3. `processos/urls.py` - Adicionar rota `/api/health/`

---

## 💡 MELHORIAS FUTURAS (FASE 2)

Após implementação estável, considerar:

1. 🔔 **Notificação Toast** quando backend voltar online
2. 📊 **Latência em tempo real** (ex: "Online - 250ms")
3. 🌐 **Status de múltiplos serviços** (DB, Redis, IA/RAG)
4. 📈 **Dashboard de saúde** (histórico de uptime)
5. 🔄 **Auto-retry** de última mensagem quando voltar online

---

**PRONTO PARA IMPLEMENTAÇÃO! 🚀**

**Próximo Passo**: Aprovar proposta → Criar branch `feat/indicador-online` → Implementar Opção 1
