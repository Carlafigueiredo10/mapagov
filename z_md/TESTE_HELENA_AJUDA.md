# 🧪 TESTE HELENA AJUDA INTELIGENTE

**Status:** Pronto para testar
**URL:** http://localhost:5173

---

## ✅ CHECKLIST DE TESTE

### 1️⃣ Teste do Fluxo Helena Primeiro (Caminho Feliz)

**Objetivo:** Validar que Helena sugere automaticamente a localização na arquitetura

**Passos:**
1. Abrir http://localhost:5173
2. Nome: "Teste Helena Ajuda"
3. Confirmar nome (Sim)
4. Área: CGBEN
5. **PONTO CRÍTICO:** Quando Helena perguntar sobre sua atividade, digitar:
   ```
   Analiso pedidos de auxílio saúde de aposentados
   ```

**Resultado Esperado:**
- ✅ Helena deve retornar sugestão estruturada tipo:
  ```
  ✅ Perfeito! Entendi sua atividade:
  📋 Macroprocesso: Gestão de Benefícios
  📋 Processo: Auxílios
  📋 Subprocesso: Auxílio Saúde
  📋 Atividade: Análise de requerimentos
  🔢 CPF: 1.2.1.1.3
  📌 Atividade encontrada no CSV oficial.

  Está correto? [✅ Confirmar] [✏️ Ajustar]
  ```
- ✅ Código CPF deve estar no formato `AREA.MACRO.PROCESSO.SUB.ATIVIDADE`
- ✅ Não deve haver erros no console do navegador
- ✅ Backend deve logar: `[INFO] helena.pop - Sugestão Helena: {...}`

---

### 2️⃣ Teste do Fallback Manual (Botão de Escape)

**Objetivo:** Validar que usuário pode escolher navegação manual

**Passos:**
1. Seguir passos 1-4 do teste anterior
2. Quando Helena perguntar sobre atividade, **clicar no botão**:
   ```
   📋 Prefiro navegar pela arquitetura oficial
   ```

**Resultado Esperado:**
- ✅ Interface muda para dropdown de Macroprocesso
- ✅ Dropdowns aparecem sequencialmente (Macro → Processo → Sub → Atividade)
- ✅ Fluxo continua normalmente após seleção

---

### 3️⃣ Teste de Não-Repetição de Códigos

**Objetivo:** Validar que Helena não sugere o mesmo código consecutivamente

**Passos:**
1. Completar um POP com Helena Ajuda (teste 1)
2. Finalizar ou salvar
3. **Iniciar NOVO POP** com a MESMA área (CGBEN)
4. Digitar atividade SIMILAR:
   ```
   Analiso auxílio saúde para pensionistas
   ```

**Resultado Esperado:**
- ✅ CPF sugerido deve ser DIFERENTE do primeiro teste
- ✅ Se atividade for muito similar, código deve ser incrementado (ex: 1.2.1.1.3 → 1.2.1.1.4)
- ✅ Backend deve logar: `[INFO] helena.pop - Código ajustado para evitar duplicata`

---

### 4️⃣ Teste de Validação com Banco de Dados

**Objetivo:** Validar que Helena verifica códigos já usados no banco

**Passos:**
1. Verificar códigos existentes no banco:
   ```bash
   python manage.py shell -c "from processos.models import POP; print([p.codigo_processo for p in POP.objects.all()[:10]])"
   ```
2. Criar novo POP e digitar atividade que gere código IGUAL a um existente
3. Observar se Helena ajusta automaticamente

**Resultado Esperado:**
- ✅ Se código existe no banco, Helena incrementa automaticamente
- ✅ Backend loga: `[INFO] helena.pop - Código X já existe no banco, usando Y`

---

### 5️⃣ Teste de Erro Gracioso (Helena Falha)

**Objetivo:** Validar fallback quando Helena não consegue entender

**Passos:**
1. Seguir passos 1-4 do teste 1
2. Digitar texto confuso/muito genérico:
   ```
   xyz abc
   ```

**Resultado Esperado:**
- ✅ Helena retorna mensagem de erro amigável
- ✅ Oferece opções: "Reformular" ou "Usar navegação manual"
- ✅ NÃO quebra a conversa
- ✅ Backend loga erro mas continua funcionando

---

## 🔍 PONTOS DE VALIDAÇÃO

### Backend (Terminal Django)

Logs esperados:
```
[INFO] helena.pop - Nova sugestão Helena para usuário: "Teste Helena Ajuda"
[INFO] helena.pop - Consultando CSV, banco e sessão para validação
[INFO] helena.pop - Sugestão Helena: {"codigo_sugerido": "1.2.1.1.3", ...}
[INFO] helena.pop - Código validado: não existe no banco nem na sessão
```

### Frontend (Console do Navegador - F12)

Verificar:
- ✅ Nenhum erro em vermelho
- ✅ Requisições para `/api/chat/` com status 200
- ✅ Resposta JSON contém `tipo_interface: "confirmacao_arquitetura"` ou `texto_com_alternativa`

---

## 📊 MÉTRICAS DE SUCESSO

Se todos os 5 testes passarem:

- ✅ **Helena Ajuda Inteligente está funcionando**
- ✅ **Sistema híbrido (Helena + Dropdowns) operacional**
- ✅ **Validação de CPF em 3 camadas funcionando**
- ✅ **Não-repetição de códigos implementada**
- ✅ **Fallback gracioso para erros**

---

## 🐛 PROBLEMAS CONHECIDOS (Não-Bloqueantes)

Se encontrar algum destes, **NÃO É BUG**:

1. **Helena sugere atividade não exatamente igual ao CSV**: Esperado, Helena pode criar novas atividades
2. **Código incrementado automaticamente**: Esperado, evita duplicatas
3. **Botão "Ajustar Manualmente" não implementado ainda**: Futuro, por enquanto confirmar ou usar fallback

---

## 🆘 SE ALGO FALHAR

### Erro 1: Helena não retorna sugestão
**Possível causa:** OpenAI API key inválida ou rate limit
**Solução:** Verificar `.env` e logs do backend

### Erro 2: Código duplicado mesmo com validação
**Possível causa:** Banco não sincronizado ou sessão não compartilhada
**Solução:** Verificar logs do backend para debug

### Erro 3: Botão "Prefiro navegar..." não aparece
**Possível causa:** Frontend não recebeu `tipo_interface: "texto_com_alternativa"`
**Solução:** Verificar resposta do backend no console (F12 → Network → api/chat/)

---

**Pronto para testar! Execute os 5 testes acima e reporte os resultados.** 🚀

**Tempo estimado:** 15-20 minutos
