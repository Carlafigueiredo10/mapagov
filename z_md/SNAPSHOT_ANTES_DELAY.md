# 📸 SNAPSHOT - Estado Antes de Implementar Sistema de DELAY

**Data**: 2025-11-01
**Branch**: feat/fase-2-edicao-granular-etapas
**Commit atual**: 67ec733 🐛 fix: corrige tela branca ao selecionar normas + erro React

---

## 🎯 OBJETIVO DA ALTERAÇÃO

Implementar sistema de mensagens sequenciais com delays usando tags `[DELAY:X]` no texto.

**Opção escolhida**: OPÇÃO A (usar sistema existente no MessageBubble)

---

## 📋 ARQUIVOS QUE SERÃO MODIFICADOS

### 1. **processos/domain/helena_produtos/helena_mapeamento.py**

**Estado atual**: Modificado (não commitado)
- Última mudança: Adicionado texto sobre humor e conduzir usuário ao fluxo

**Alterações planejadas**:
- Modificar mensagem de introdução detalhada para incluir tags `[DELAY:1500]`
- Arquivo: Método que gera mensagem longa sobre explicação do POP

**Backup necessário**: ✅ SIM (tem mudanças não commitadas)

---

### 2. **processos/app/helena_core.py** (OPCIONAL - apenas limpeza)

**Estado atual**: Não modificado desde último commit

**Alterações planejadas** (OPCIONAL):
- Adicionar função helper para limpar tags `[DELAY:X]` antes de salvar no banco
- Apenas se necessário para evitar poluição do histórico

**Backup necessário**: ⚠️ TALVEZ

---

## 🔍 VALIDAÇÃO DO SISTEMA EXISTENTE

### MessageBubble.tsx - Linhas 29-57

```typescript
// ✅ Detectar mensagens com delay e quebrar em partes
const mensagemTexto = message.mensagem || '';
const temDelay = mensagemTexto.includes('[DELAY:');
const partesMensagem = temDelay
  ? mensagemTexto.split(/\[DELAY:\d+\]/).map(p => p.trim()).filter(p => p)
  : mensagemTexto ? [mensagemTexto] : [];

// ✅ Efeito para mostrar partes progressivamente
useEffect(() => {
  if (partesMensagem.length === 0) {
    setPartesVisiveis([]);
    return;
  }

  if (temDelay && partesMensagem.length > 1) {
    // Mostrar primeira parte imediatamente
    setPartesVisiveis([partesMensagem[0]]);

    // Mostrar partes seguintes com delay
    partesMensagem.slice(1).forEach((parte, index) => {
      setTimeout(() => {
        setPartesVisiveis(prev => [...prev, parte]);
      }, (index + 1) * 1000); // 1 segundo entre cada parte
    });
  } else {
    setPartesVisiveis(partesMensagem);
  }
}, [mensagemTexto]);
```

**Status**: ✅ FUNCIONAL - Sistema já implementado!

---

## 🎯 EXEMPLO DE ALTERAÇÃO

### Antes:
```python
def gerar_introducao_detalhada(self):
    return """Opa, você quer mais detalhes? 😊

Eu amei, porque adoro conversar!

Então vamos com calma, que eu te explico tudo direitinho.

Nesse chat, a gente vai mapear a sua atividade..."""
```

### Depois:
```python
def gerar_introducao_detalhada(self):
    return """Opa, você quer mais detalhes? 😊
[DELAY:1500]
Eu amei, porque adoro conversar!
[DELAY:1500]
Então vamos com calma, que eu te explico tudo direitinho.
[DELAY:1500]
Nesse chat, a gente vai mapear a sua atividade..."""
```

---

## 🚨 RISCOS IDENTIFICADOS

1. **Tags no histórico**: Mensagens salvas no banco terão tags `[DELAY:]` visíveis
   - **Mitigação**: Adicionar limpeza no `helena_core.py` antes de salvar
   - **Impacto se não mitigar**: Médio (não quebra, apenas polui)

2. **Regex do MessageBubble**: Split por `/\[DELAY:\d+\]/`
   - **Validado**: ✅ Funciona corretamente
   - **Impacto**: Zero

3. **Timing fixo**: MessageBubble usa 1000ms, não o valor da tag
   - **Descoberta**: ⚠️ MessageBubble ignora o número dentro do DELAY!
   - **Correção necessária**: Sim, se quiser delays personalizados
   - **Impacto se não corrigir**: Baixo (apenas usa 1s para todos)

---

## 🔧 CORREÇÃO ADICIONAL DESCOBERTA

MessageBubble linha 52 usa delay fixo de 1000ms:
```typescript
}, (index + 1) * 1000); // ← FIXO!
```

Para usar o valor da tag `[DELAY:1500]`:
```typescript
// Extrair delays da mensagem original
const delays = mensagemTexto.match(/\[DELAY:(\d+)\]/g)?.map(
  match => parseInt(match.match(/\d+/)[0])
) || [];

// Usar delay específico
setTimeout(() => {
  setPartesVisiveis(prev => [...prev, parte]);
}, delays[index] || 1000);
```

**Incluir esta correção?**: ⚠️ A DECIDIR

---

## 📦 PLANO DE REVERSÃO

### Se você disser "volta":

1. **Reverter helena_mapeamento.py**:
   ```bash
   git checkout -- processos/domain/helena_produtos/helena_mapeamento.py
   ```

2. **Reverter helena_core.py** (se modificado):
   ```bash
   git checkout -- processos/app/helena_core.py
   ```

3. **Reverter MessageBubble.tsx** (se modificado):
   ```bash
   git checkout -- frontend/src/components/Helena/MessageBubble.tsx
   ```

4. **Deletar este arquivo de snapshot**:
   ```bash
   rm SNAPSHOT_ANTES_DELAY.md
   ```

---

## ✅ CHECKLIST PRÉ-IMPLEMENTAÇÃO

- [x] Git status verificado
- [x] Arquivos modificados identificados
- [x] Sistema existente validado
- [x] Riscos mapeados
- [x] Plano de reversão documentado
- [x] Snapshot criado
- [ ] Backup dos arquivos modificados
- [ ] Implementação
- [ ] Testes

---

## 📝 NOTAS IMPORTANTES

1. **Arquivos .pyc**: Ignorar, são gerados automaticamente
2. **staticfiles/**: Arquivos estáticos compilados, ignorar
3. **db.sqlite3**: Banco de desenvolvimento, não versionar mudanças
4. **Documentos .md não commitados**: Manter como estão

---

**ESTADO**: Pronto para implementação
**PRÓXIMO PASSO**: Criar backup manual dos arquivos que serão modificados
