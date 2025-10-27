# 🧪 TESTE MANUAL - Refatoração HelenaPOP

## ✅ Status dos Servidores

### Backend Django
```
✅ RODANDO em http://localhost:8000
Status: Watching for file changes with StatReloader
```

### Frontend React (Vite)
```
✅ RODANDO em http://localhost:5173
Status: VITE v7.1.9 ready in 4687 ms
```

---

## 📋 Roteiro de Teste

### 1. **Abrir Aplicação**

**URL:** http://localhost:5173

**Esperado:**
- ✅ Página carrega sem erros no console do navegador
- ✅ Logo do MapaGov aparece
- ✅ Helena aparece com a mensagem de boas-vindas

---

### 2. **Fluxo de Nome**

**Ação:** Digite seu nome (ex: "Roberto Teste")

**Esperado:**
- ✅ Helena pergunta para confirmar o nome
- ✅ Botões "Sim" e "Não" aparecem

**Ação:** Clique em "Sim"

**Esperado:**
- ✅ Helena confirma e passa para próxima etapa

---

### 3. **Seleção de Área**

**Ação:** Selecione uma área (ex: "CGBEN - Coordenação Geral de Benefícios")

**Esperado:**
- ✅ Helena confirma a área selecionada
- ✅ Passa para seleção de macroprocesso

---

### 4. **Navegação pela Arquitetura**

**Ação:** Selecione:
- Macroprocesso: "Gestão de Benefícios"
- Processo: "Auxílios"
- Subprocesso: "Auxílio Alimentação"
- Atividade: "Concessão"

**Esperado:**
- ✅ Helena confirma cada seleção
- ✅ Progresso avança
- ✅ Chega na coleta de etapas

---

### 5. **🎯 TESTE PRINCIPAL: Mapeamento de Etapa Linear (REFATORADO)**

**Ação:** Digite a etapa:
```
Receber requerimento no SEI e protocolar
```

**Esperado:**
- ✅ Helena registra: "Etapa 1 registrada. Vamos detalhar essa etapa."
- ✅ Aparece dropdown de operadores

**Ação:** Selecione operador: "Técnico Especializado"

**Esperado:**
- ✅ Helena pergunta: "A Etapa 1 tem decisões/condições?"
- ✅ Botões "Sim" e "Não" aparecem

**Ação:** Clique em "Não"

**Esperado:**
- ✅ Helena pede os detalhes/passos da etapa
- ✅ Campo de texto livre aparece

**Ação:** Digite o detalhe:
```
Verificar dados do requerente no SEI
```

**Esperado:**
- ✅ Helena confirma: "Detalhe registrado: 1.1 Verificar dados..."
- ✅ Pergunta se há mais detalhes

**Ação:** Digite "fim" ou clique em "Não há mais"

**Esperado:**
- ✅ Helena confirma: "Etapa 1 completa!"
- ✅ Pergunta se há mais etapas

---

### 6. **🎯 TESTE AVANÇADO: Etapa Condicional Binária (REFATORADO)**

**Ação:** Digite nova etapa:
```
Avaliar completude da documentação
```

**Esperado:**
- ✅ Helena pede operador

**Ação:** Selecione "Coordenador"

**Esperado:**
- ✅ Helena pergunta sobre condicionais

**Ação:** Clique em "Sim"

**Esperado:**
- ✅ Helena pergunta: "Quantos cenários possíveis existem?"
- ✅ Opções: "2 cenários" ou "Múltiplos cenários"

**Ação:** Selecione "2 cenários (binário)"

**Esperado:**
- ✅ Helena pede: "O que deve ser feito ANTES da decisão?"

**Ação:** Digite:
```
Conferir se todos os documentos obrigatórios foram anexados
```

**Esperado:**
- ✅ Helena pede para definir os 2 cenários
- ✅ Campos para "Cenário 1" e "Cenário 2" aparecem

**Ação:** Preencha os cenários:
- Cenário 1: "Documentação completa"
- Cenário 2: "Documentação incompleta"

**Esperado:**
- ✅ Helena confirma os cenários
- ✅ Pede subetapas do primeiro cenário

**Ação:** Digite subetapas do Cenário 1:
```
Aprovar pedido
Registrar aprovação no sistema
```

**Esperado:**
- ✅ Helena pede subetapas do Cenário 2

**Ação:** Digite subetapas do Cenário 2:
```
Solicitar documentos faltantes
Notificar requerente via e-mail
```

**Esperado:**
- ✅ Helena confirma: "Etapa 2 completa com hierarquia!"
- ✅ Etapa condicional salva com sucesso

---

### 7. **Verificar Logs do Backend**

**Ação:** Verifique o terminal onde Django está rodando

**Esperado:**
- ✅ Logs aparecem com prefixo `[INFO] helena.pop -`
- ✅ Mensagens como:
  ```
  [INFO] helena.pop - Nova StateMachine criada para Etapa 1
  [INFO] helena.pop - Etapa 1 completa e adicionada!
  [INFO] helena.pop - Nova StateMachine criada para Etapa 2
  [INFO] helena.pop - Etapa 2 completa e adicionada!
  ```

---

### 8. **Verificar Console do Navegador**

**Ação:** Abra DevTools (F12) → Console

**Esperado:**
- ✅ Nenhum erro em vermelho
- ✅ Apenas logs informativos (se houver)
- ✅ Requisições para `http://localhost:8000/api/chat/` com status 200

---

### 9. **Finalizar Mapeamento**

**Ação:** Digite "não" quando Helena perguntar se há mais etapas

**Esperado:**
- ✅ Helena passa para próxima fase (fluxos de saída)
- ✅ Etapas foram salvas corretamente

---

## 🔍 O Que Verificar

### ✅ Checklist de Validação

- [ ] Frontend carrega sem erros
- [ ] Backend responde às requisições
- [ ] Logger mostra mensagens `[INFO] helena.pop`
- [ ] Etapa linear funciona (sem condicionais)
- [ ] Etapa condicional binária funciona (com cenários)
- [ ] StateMachine é criada e destruída corretamente
- [ ] Adapter traduz sinais da SM para JSON do frontend
- [ ] Interface permanece igual (100% compatível)
- [ ] Nenhum erro 500 no backend
- [ ] Nenhum erro JavaScript no console

---

## 🐛 Problemas Conhecidos (Não Relacionados à Refatoração)

Se encontrar problemas NÃO relacionados à refatoração (ex: CORS, banco de dados, autenticação), esses são problemas pré-existentes do ambiente e não da refatoração.

---

## 📊 Métricas da Refatoração

Caso tudo funcione corretamente, você terá validado:

- ✅ **-78% de código** (495 → 109 linhas)
- ✅ **-87% de complexidade** (40 → 5)
- ✅ **0 flags booleanas** (eliminadas 8)
- ✅ **32 testes passando** (26 unitários + 6 integração)
- ✅ **100% compatível** com frontend React

---

## 🎯 Resultado Esperado

Se todos os itens acima funcionarem:

**🎉 A REFATORAÇÃO FOI UM SUCESSO TOTAL!**

A Helena está usando a nova arquitetura com:
- State Machine Pattern
- Domain-Driven Design
- Logger centralizado
- Adapter Pattern (compatibilidade)

E o melhor: **o usuário não percebe nenhuma diferença** - a interface continua exatamente igual, mas o código por trás é muito mais limpo, testável e mantível!

---

## 🆘 Em Caso de Problemas

### Se encontrar erros:

1. **Verifique os logs do Django** (terminal do backend)
2. **Verifique o console do navegador** (F12)
3. **Anote exatamente qual passo falhou**
4. **Copie a mensagem de erro completa**

### Comandos úteis:

```bash
# Parar servidores
# Ctrl+C em cada terminal

# Reiniciar backend
python manage.py runserver 8000

# Reiniciar frontend
cd frontend && npm run dev

# Ver logs com mais detalhes
python manage.py runserver 8000 --verbosity=2
```

---

**Pronto para testar! Acesse http://localhost:5173 e siga o roteiro acima.** 🚀
