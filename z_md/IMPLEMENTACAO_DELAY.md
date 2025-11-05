# 🎯 IMPLEMENTAÇÃO - Sistema de DELAY

**Data**: 2025-11-01
**Status**: PRONTO PARA IMPLEMENTAR

---

## 📍 MENSAGENS IDENTIFICADAS PARA ADICIONAR DELAY

### Arquivo: `processos/domain/helena_produtos/helena_pop.py`

#### 1. **Linha 1654-1674** - Explicação Longa (ESCOLHA_TIPO_EXPLICACAO)
```python
resposta = (
    f"Opa, você quer mais detalhes\n"
    f"Eu amei, porque adoro conversar 😄\n"
    f"Então vamos com calma, que eu te explico tudo direitinho.\n\n"
    # ... resto da mensagem longa
)
```

#### 2. **Linha 1819-1839** - Explicação Longa (EXPLICACAO)
```python
resposta = (
    f"Opa, você quer mais detalhes\n"
    f"Eu amei, porque adoro conversar 😄\n"
    f"Então vamos com calma, que eu te explico tudo direitinho.\n\n"
    # ... resto da mensagem longa
)
```

**Observação**: São a MESMA mensagem em dois lugares diferentes! Podemos criar uma função helper.

---

## 🔨 PLANO DE IMPLEMENTAÇÃO

### PASSO 1: Criar função helper para mensagem longa

```python
def _gerar_explicacao_longa_com_delay(self, nome_usuario: str = None) -> str:
    """
    Gera mensagem de explicação longa com delays progressivos.

    Quebra a mensagem em 4 partes:
    1. Introdução empática (0ms)
    2. Explicação do que será feito (1500ms)
    3. Detalhamento das etapas (1500ms)
    4. Fechamento motivacional (1500ms)
    """
    return (
        f"Opa, você quer mais detalhes? 😊[DELAY:1500]"
        f"Eu amei, porque adoro conversar![DELAY:1500]"
        f"Então vamos com calma, que eu te explico tudo direitinho.\n\n"
        f"Nesse chat, a gente vai mapear a sua atividade:\n\n"
        f"aquilo que você faz todos os dias (ou quase), a rotina real do seu trabalho.\n\n"
        f"A ideia é preencher juntos o formulário de Procedimento Operacional Padrão, o famoso POP, "
        f"que tá aí do lado 👉\n"
        f"Dá uma olhadinha! Nossa meta é deixar esse POP prontinho, claro e útil pra todo mundo que "
        f"trabalha com você. ✅[DELAY:1500]"
        f"\n\nEu vou te perguntar:\n"
        f"🧭 em qual área você atua,\n"
        f"🧩 te ajudar com a parte mais burocrática — macroprocesso, processo, subprocesso e atividade,\n"
        f"📘 e criar o \"CPF\" do seu processo (a gente chama de CAP, Código na Arquitetura do Processo).\n\n"
        f"Depois, vamos falar sobre os sistemas que você usa e as normas que regem sua atividade.\n"
        f"Nessa parte, vou até te apresentar minha amiga do Sigepe Legis IA — ela é especialista em achar "
        f"a norma certa no meio de tanta lei e portaria 🤖📜[DELAY:1500]"
        f"\n\nPor fim, vem a parte mais detalhada: você vai me contar passo a passo o que faz no dia a dia.\n\n"
        f"Pode parecer demorado, mas pensa assim: quanto melhor você mapear agora, menos retrabalho vai "
        f"ter depois — e o seu processo vai ficar claro, seguro e fácil de ensinar pra quem chegar novo. 💪\n\n"
        f"Tudo certo até aqui?"
    )
```

### PASSO 2: Atualizar linha 1654 (usar helper)

```python
def _processar_escolha_tipo_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
    """Processa escolha entre explicação curta ou longa"""
    msg_lower = mensagem.lower().strip()

    # Explicação detalhada/longa
    if any(palavra in msg_lower for palavra in ['detalhada', 'longa', 'detalhes', 'completa']):
        sm.estado = EstadoPOP.EXPLICACAO_LONGA
        resposta = self._gerar_explicacao_longa_com_delay(sm.nome_usuario)  # ← USAR HELPER
        return resposta, sm
    # ... resto do código
```

### PASSO 3: Atualizar linha 1819 (usar helper)

```python
def _processar_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
    # ...
    elif 'detalhes' in msg_lower or 'detalhe' in msg_lower or ('não' in msg_lower or 'nao' in msg_lower):
        sm.estado = EstadoPOP.EXPLICACAO_LONGA
        resposta = self._gerar_explicacao_longa_com_delay(sm.nome_usuario)  # ← USAR HELPER
    # ... resto do código
```

---

## ⚠️ PROBLEMA DETECTADO: Timing Fixo no MessageBubble

### MessageBubble.tsx linha 52:
```typescript
}, (index + 1) * 1000); // ← IGNORA O VALOR DO DELAY!
```

### CORREÇÃO NECESSÁRIA:

```typescript
// Extrair delays da mensagem original
const extractDelays = (text: string): number[] => {
  const matches = text.match(/\[DELAY:(\d+)\]/g);
  if (!matches) return [];
  return matches.map(match => {
    const num = match.match(/\d+/);
    return num ? parseInt(num[0]) : 1000;
  });
};

const delays = extractDelays(mensagemTexto);

// Usar delay específico ao mostrar partes
partesMensagem.slice(1).forEach((parte, index) => {
  const delayMs = delays[index] || 1000; // Fallback para 1000ms
  setTimeout(() => {
    setPartesVisiveis(prev => [...prev, parte]);
  }, delayMs);
});
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Criar função `_gerar_explicacao_longa_com_delay` em helena_pop.py
- [ ] Atualizar linha 1654 (escolha tipo explicação)
- [ ] Atualizar linha 1819 (explicação)
- [ ] Corrigir MessageBubble.tsx para usar delays reais (não fixo 1000ms)
- [ ] Testar com usuário real
- [ ] Validar que delays funcionam corretamente

---

## 🎬 ORDEM DE EXECUÇÃO

1. ✅ helena_pop.py (backend)
2. ✅ MessageBubble.tsx (frontend - correção de timing)
3. ✅ Testar no navegador

---

**PRÓXIMO COMANDO**: "pode implementar"
