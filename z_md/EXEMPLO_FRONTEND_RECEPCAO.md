# 🎨 Exemplo de Integração Frontend - Helena Recepção

**Objetivo:** Mostrar como processar o JSON estruturado retornado pela API `/api/chat-recepcao/`

---

## 📡 Resposta da API (Exemplo)

### Caso 1: Redirecionamento para P1

**Request:**
```javascript
POST /api/chat-recepcao/
{
  "message": "Quero mapear um processo",
  "session_id": "abc-123"
}
```

**Response:**
```json
{
  "acao": "redirecionar",
  "produto_id": "P1",
  "produto_nome": "Gerador de POP",
  "produto_link": "/chat",
  "mensagem": "Perfeito! Para mapear esse processo, acesse o **Gerador de POP**. Clique no botão abaixo para começar! 🎯",
  "motivo_bloqueio": null,
  "success": true
}
```

---

## 🔧 Integração com React/TypeScript

### Passo 1: Definir Tipo TypeScript

```typescript
// frontend/src/types/helena.ts

export interface RespostaRecepcao {
  acao: 'redirecionar' | 'informar' | 'bloquear';
  produto_id: string | null;
  produto_nome: string | null;
  produto_link: string | null;
  mensagem: string;
  motivo_bloqueio: string | null;
  success: boolean;
}
```

### Passo 2: Atualizar Serviço API

```typescript
// frontend/src/services/helenaApi.ts

import axios from 'axios';
import { RespostaRecepcao } from '../types/helena';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const helenaApi = {
  chatRecepcao: async (mensagem: string, sessionId: string): Promise<RespostaRecepcao> => {
    const response = await axios.post<RespostaRecepcao>(
      `${API_BASE_URL}/api/chat-recepcao/`,
      {
        message: mensagem,
        session_id: sessionId
      }
    );
    return response.data;
  }
};
```

### Passo 3: Componente de Chat (Exemplo)

```tsx
// frontend/src/components/ChatRecepcao.tsx

import React, { useState } from 'react';
import { helenaApi } from '../services/helenaApi';
import { RespostaRecepcao } from '../types/helena';
import { useNavigate } from 'react-router-dom';

export const ChatRecepcao: React.FC = () => {
  const [mensagem, setMensagem] = useState('');
  const [historico, setHistorico] = useState<Array<{
    tipo: 'user' | 'helena';
    conteudo: string;
    resposta?: RespostaRecepcao;
  }>>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const enviarMensagem = async () => {
    if (!mensagem.trim()) return;

    // Adicionar mensagem do usuário ao histórico
    setHistorico(prev => [...prev, { tipo: 'user', conteudo: mensagem }]);

    setLoading(true);
    try {
      const resposta = await helenaApi.chatRecepcao(
        mensagem,
        `session-${Date.now()}`  // ou usar sessionId persistente
      );

      // Adicionar resposta da Helena ao histórico
      setHistorico(prev => [...prev, {
        tipo: 'helena',
        conteudo: resposta.mensagem,
        resposta: resposta
      }]);

      setMensagem('');
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setHistorico(prev => [...prev, {
        tipo: 'helena',
        conteudo: '⚠️ Ocorreu um erro. Tente novamente.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const redirecionarProduto = (link: string) => {
    navigate(link);
  };

  return (
    <div className="chat-recepcao">
      {/* Histórico de mensagens */}
      <div className="chat-historico">
        {historico.map((item, index) => (
          <div key={index} className={`chat-mensagem chat-mensagem-${item.tipo}`}>
            <div className="mensagem-texto">{item.conteudo}</div>

            {/* Renderizar botão de redirecionamento se aplicável */}
            {item.tipo === 'helena' && item.resposta?.acao === 'redirecionar' && (
              <button
                className="btn-redirecionar"
                onClick={() => redirecionarProduto(item.resposta!.produto_link!)}
              >
                🚀 Acessar {item.resposta.produto_nome}
              </button>
            )}

            {/* Mostrar aviso se bloqueado */}
            {item.tipo === 'helena' && item.resposta?.acao === 'bloquear' && (
              <div className="alerta-bloqueio">
                ⚠️ {item.resposta.motivo_bloqueio}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input de mensagem */}
      <div className="chat-input">
        <input
          type="text"
          value={mensagem}
          onChange={(e) => setMensagem(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && enviarMensagem()}
          placeholder="Digite sua mensagem..."
          disabled={loading}
        />
        <button onClick={enviarMensagem} disabled={loading}>
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
};
```

### Passo 4: Estilos CSS (Exemplo)

```css
/* frontend/src/components/ChatRecepcao.module.css */

.chat-recepcao {
  display: flex;
  flex-direction: column;
  height: 500px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.chat-historico {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f9f9f9;
}

.chat-mensagem {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
  max-width: 70%;
}

.chat-mensagem-user {
  background-color: #007bff;
  color: white;
  margin-left: auto;
  text-align: right;
}

.chat-mensagem-helena {
  background-color: white;
  border: 1px solid #ddd;
}

.mensagem-texto {
  margin-bottom: 8px;
  white-space: pre-wrap;
}

.btn-redirecionar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: transform 0.2s;
}

.btn-redirecionar:hover {
  transform: scale(1.05);
}

.alerta-bloqueio {
  background-color: #fff3cd;
  color: #856404;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ffeeba;
  margin-top: 8px;
}

.chat-input {
  display: flex;
  padding: 16px;
  border-top: 1px solid #ddd;
  background-color: white;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
}

.chat-input button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
```

---

## 🎯 Exemplos de Renderização

### Exemplo 1: Redirecionamento para P1

**Resposta da API:**
```json
{
  "acao": "redirecionar",
  "produto_id": "P1",
  "produto_nome": "Gerador de POP",
  "produto_link": "/chat",
  "mensagem": "Perfeito! Para mapear esse processo, acesse o **Gerador de POP**."
}
```

**Renderizado como:**

```
┌─────────────────────────────────────────────┐
│ Helena                                      │
│                                             │
│ Perfeito! Para mapear esse processo,       │
│ acesse o **Gerador de POP**.               │
│                                             │
│ ┌─────────────────────────────────────┐    │
│ │  🚀 Acessar Gerador de POP          │    │
│ └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Exemplo 2: Resposta Informativa (sem botão)

**Resposta da API:**
```json
{
  "acao": "informar",
  "produto_id": null,
  "produto_nome": null,
  "produto_link": null,
  "mensagem": "Governança corporativa é o sistema de regras..."
}
```

**Renderizado como:**

```
┌─────────────────────────────────────────────┐
│ Helena                                      │
│                                             │
│ Governança corporativa é o sistema de      │
│ regras e práticas que direcionam a gestão  │
│ de uma organização...                      │
└─────────────────────────────────────────────┘
```

### Exemplo 3: Bloqueio (spam)

**Resposta da API:**
```json
{
  "acao": "bloquear",
  "produto_id": null,
  "produto_nome": null,
  "produto_link": null,
  "mensagem": "Por favor, envie mensagens mais curtas.",
  "motivo_bloqueio": "Mensagem excede 500 caracteres"
}
```

**Renderizado como:**

```
┌─────────────────────────────────────────────┐
│ Helena                                      │
│                                             │
│ Por favor, envie mensagens mais curtas.    │
│                                             │
│ ⚠️ Mensagem excede 500 caracteres          │
└─────────────────────────────────────────────┘
```

---

## 🧪 Como Testar no Frontend

### Passo 1: Verificar que API está rodando
```bash
# Terminal 1: Backend
python manage.py runserver 8000
```

### Passo 2: Iniciar frontend
```bash
# Terminal 2: Frontend
cd frontend
npm run dev
```

### Passo 3: Testar casos de uso

| Mensagem | Esperado |
|----------|----------|
| "Quero mapear um processo" | Botão "Acessar Gerador de POP" aparece |
| "Como identifico riscos?" | Botão "Acessar Análise de Riscos" aparece |
| "O que é governança?" | Apenas texto (sem botão) |
| Mensagem com 600 caracteres | Alerta de bloqueio |

---

## 🚀 Melhorias Futuras

### 1. **Auto-redirecionamento** (opcional)
Após 3 segundos sem clique no botão, redirecionar automaticamente:

```tsx
useEffect(() => {
  if (ultimaResposta?.acao === 'redirecionar') {
    const timer = setTimeout(() => {
      navigate(ultimaResposta.produto_link!);
    }, 3000);

    return () => clearTimeout(timer);
  }
}, [ultimaResposta]);
```

### 2. **Analytics**
Rastrear cliques nos botões de redirecionamento:

```tsx
const redirecionarProduto = (link: string, produtoId: string) => {
  // Enviar evento de analytics
  gtag('event', 'helena_redirecionamento', {
    produto_id: produtoId,
    produto_link: link
  });

  navigate(link);
};
```

### 3. **Markdown no `mensagem`**
Renderizar markdown (ex: **negrito**) na mensagem:

```tsx
import ReactMarkdown from 'react-markdown';

<ReactMarkdown>{item.conteudo}</ReactMarkdown>
```

---

**Documento criado por:** Claude Code
**Para:** Frontend Developer
**Última atualização:** 2025-10-18
