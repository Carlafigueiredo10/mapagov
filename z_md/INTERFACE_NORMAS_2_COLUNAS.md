# Interface de Normas - Layout 2 Colunas (UX Redesign)

## 📋 Resumo Executivo

**Data:** 2025-10-22
**Status:** ✅ Implementado e pronto para teste
**Versão:** 3.0 - Layout 2 Colunas Equilibrado

### O que foi feito?

Redesenhamos completamente a **interface de seleção de normas** seguindo princípios de UX/UI modernos, transformando uma lista burocrática em um **ambiente de descoberta** com duas experiências complementares.

---

## 🎯 Problema Anterior (v2.2)

### Interface Antiga:
- ❌ Lista vertical única (sugestões → botão expandir → acordeão → manual)
- ❌ Experiência linear e burocrática
- ❌ Usuário precisa rolar muito para encontrar opções
- ❌ Não destaca o poder da IA (sugestões escondidas entre muitas opções)
- ❌ Botão "Visualizar todas" pouco intuitivo

### Nova Interface (v3.0):
- ✅ **Layout 2 colunas** equilibrado e espacial
- ✅ **Esquerda (💡 Sugestões da Helena):** IA ajuda proativamente
- ✅ **Direita (📚 Outras Normas):** Usuário explora autonomamente
- ✅ **Campo de busca** integrado para filtragem rápida
- ✅ **Botão IA Legis** destacado com tooltip explicativo
- ✅ **Rodapé integrado** dentro do container com contador e ações
- ✅ **Responsivo mobile** (vira layout vertical automático)

---

## 🎨 Proposta Detalhada

### 💙 Coluna Esquerda — "Sugestões Inteligentes"

**Título:** "💡 Sugestões da Helena"
**Descrição:** "Normas mais prováveis para o seu processo"

**Conteúdo:**
- Lista de 2-3 cards de normas com:
  - Badge de grupo (🩺 Benefícios, 👥 Pessoas, etc.)
  - Nome curto + nome completo
  - Artigos
  - Relevância em %
- **Botão:** "✓ Selecionar Todas as Sugestões"

**Destaque IA Legis:**
- Container com borda tracejada roxa
- **Tooltip:** "💡 A IA do Legis procura automaticamente outras normas relacionadas"
- **Botão:** "🔍 Buscar novas sugestões no Sigepe Legis IA"
  - Gradiente roxo
  - Abre nova aba para IA Legis

**Função cognitiva:** Reforçar confiança ("ela já pesquisou pra mim")
**Emoção desejada:** Sensação de apoio e economia de esforço

### 💼 Coluna Direita — "Explorar e Adicionar Manualmente"

**Título:** "📚 Outras Normas por Tema"
**Descrição:** "Explore nossa biblioteca completa"

**Conteúdo:**
1. **Campo de Busca:**
   - Ícone de lupa à esquerda
   - Placeholder: "🔎 Digite o nome ou número da norma"
   - Botão "✕" para limpar (quando digitando)
   - Filtragem em tempo real

2. **Acordeões dos Grupos:**
   - 6 grupos DECIPEX com emojis (vindos do backend)
   - Contador de normas em cada grupo
   - Clique para expandir/recolher
   - Normas pequenas com checkbox

3. **Botão Adicionar Manual:**
   - "➕ Adicionar Norma Manualmente"
   - Borda tracejada verde
   - Expande campos de input

4. **Seção de Normas Manuais:**
   - Input para digitar norma livre
   - Botão "➕ Adicionar Outro Campo"
   - Botão "✕" para remover campos

**Função cognitiva:** Autonomia e completude ("posso ir além do que o sistema sugeriu")
**Emoção desejada:** Empoderamento e controle

---

## 🛠️ Implementação Técnica

### Arquivo Modificado:

**`frontend/src/components/Helena/InterfaceNormas.tsx`** (~920 linhas)

### Principais Mudanças:

#### 1. Imports
```typescript
import { ChevronDown, ChevronRight, Search } from "lucide-react";
```

#### 2. Estados Adicionados
```typescript
const [termoBusca, setTermoBusca] = useState<string>('');
```

#### 3. Lógica de Filtragem
```typescript
const categoriasFiltradas = useMemo(() => {
  if (!termoBusca.trim()) {
    return categorias;
  }

  const termo = termoBusca.toLowerCase();
  const resultado: Record<string, Norma[]> = {};

  Object.entries(categorias).forEach(([categoria, normas]) => {
    const normasFiltradas = normas.filter(norma =>
      norma.nome_curto.toLowerCase().includes(termo) ||
      norma.nome_completo.toLowerCase().includes(termo) ||
      norma.artigos.toLowerCase().includes(termo)
    );

    if (normasFiltradas.length > 0) {
      resultado[categoria] = normasFiltradas;
    }
  });

  return resultado;
}, [categorias, termoBusca]);
```

#### 4. Estrutura JSX
```tsx
<div className="interface-container fade-in">
  {/* Cabeçalho Unificado */}
  <div className="interface-title">📚 Normas e Dispositivos Legais</div>
  <div className="interface-subtitle">
    Selecione as normas que regulamentam esta atividade.
    À esquerda, veja nossas sugestões inteligentes.
    À direita, explore outras opções.
  </div>

  {/* Layout 2 Colunas */}
  <div className="two-columns-layout">

    {/* 🩵 COLUNA ESQUERDA */}
    <div className="column-left">
      <div className="column-header">
        <h3>💡 Sugestões da Helena</h3>
        <p className="column-desc">Normas mais prováveis para o seu processo</p>
      </div>

      {/* Sugestões */}
      <div className="normas-list">...</div>
      <button className="btn-selecionar-sugestoes">
        ✓ Selecionar Todas as Sugestões
      </button>

      {/* Botão IA Legis */}
      <div className="ia-legis-container">
        <div className="ia-legis-tooltip">
          💡 A IA do Legis procura automaticamente outras normas relacionadas
        </div>
        <button className="btn-ia-legis">
          🔍 Buscar novas sugestões no Sigepe Legis IA
        </button>
      </div>
    </div>

    {/* 💼 COLUNA DIREITA */}
    <div className="column-right">
      <div className="column-header">
        <h3>📚 Outras Normas por Tema</h3>
        <p className="column-desc">Explore nossa biblioteca completa</p>
      </div>

      {/* Campo de Busca */}
      <div className="search-container">
        <Search size={18} className="search-icon" />
        <input
          className="search-input"
          placeholder="🔎 Digite o nome ou número da norma"
          value={termoBusca}
          onChange={(e) => setTermoBusca(e.target.value)}
        />
        {termoBusca && (
          <button className="clear-search" onClick={() => setTermoBusca('')}>
            ✕
          </button>
        )}
      </div>

      {/* Acordeão Categorias (filtrado) */}
      <div className="categorias-acordeao">...</div>

      {/* Botão Adicionar Manual */}
      <button className="btn-adicionar-manual">
        ➕ Adicionar Norma Manualmente
      </button>

      {/* Seção Normas Manuais (expansível) */}
      {mostrarNormasManuais && (
        <div className="normas-manuais-section">...</div>
      )}
    </div>
  </div>

  {/* Rodapé Integrado */}
  <div className="footer-actions">
    <div className="contador-e-limpar">
      <div className="contador-normas">
        {normasSelecionadas.length} norma(s) selecionada(s)
      </div>
      {normasSelecionadas.length > 0 && (
        <button className="btn-limpar-selecao" onClick={limparSelecao}>
          🗑️ Limpar Seleção
        </button>
      )}
    </div>

    <div className="action-buttons">
      <button className="btn-interface btn-secondary" onClick={() => onConfirm('nao sei')}>
        Não Sei
      </button>
      <button className="btn-interface btn-primary" onClick={handleConfirm}>
        Confirmar
      </button>
    </div>
  </div>
</div>
```

#### 5. CSS Principal

**Layout 2 Colunas:**
```css
.two-columns-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 0;
}

@media (max-width: 968px) {
  .two-columns-layout {
    grid-template-columns: 1fr; /* Mobile: 1 coluna */
  }
}
```

**Fundos Diferenciados:**
```css
.column-left {
  background: #f9fafc; /* Cinza muito claro */
  border-radius: 12px;
  padding: 1.5rem;
  border: 2px solid #e0e6ed;
}

.column-right {
  background: #ffffff; /* Branco puro */
  border-radius: 12px;
  padding: 1.5rem;
  border: 2px solid #e0e6ed;
}
```

**Footer Integrado (FIX v3.0.1):**
```css
/* Rodapé DENTRO do container (não fixed na viewport) */
.footer-actions {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 3px solid #1351B4;
}
```

**❌ ERRO INICIAL (v3.0.0 - CORRIGIDO):**
```css
/* NÃO USE - Footer fixo sai do chat e vai para borda da tela */
.sticky-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}
```

**Botão IA Legis:**
```css
.ia-legis-container {
  margin-top: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
  border-radius: 8px;
  border: 2px dashed #667eea; /* Borda tracejada roxa */
}

.ia-legis-tooltip {
  text-align: center;
  font-size: 0.8rem;
  color: #5a67d8;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.btn-ia-legis {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-ia-legis:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}
```

**Campo de Busca:**
```css
.search-container {
  position: relative;
  margin-bottom: 1rem;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 2.5rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #1351B4;
  box-shadow: 0 0 0 3px rgba(19, 81, 180, 0.1);
}

.clear-search {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.clear-search:hover {
  background: #c82333;
}
```

**Botão Adicionar Manual:**
```css
.btn-adicionar-manual {
  width: 100%;
  padding: 0.75rem;
  background: white;
  color: #28a745;
  border: 2px dashed #28a745;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 1rem;
}

.btn-adicionar-manual:hover {
  background: #28a745;
  color: white;
  border-style: solid;
}
```

---

## 🚀 Como Testar

### Passo 1: Garantir servidores rodando

**Terminal 1 (Backend):**
```bash
# Reiniciar se não viu mudanças anteriores
python manage.py runserver 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev  # Porta 5173
# Ou use o build que acabou de ser feito
```

### Passo 2: Navegar até Normas

1. Acesse: http://localhost:5173
2. Inicie conversa com Helena POP
3. Preencha campos até chegar em **"📚 Normas e Dispositivos Legais"**

### Passo 3: Verificar novo layout

**Coluna Esquerda (💡 Sugestões):**
- ✅ Ver 2-3 cards com badges de grupo coloridos
- ✅ Botão "✓ Selecionar Todas as Sugestões"
- ✅ Container tracejado roxo com IA Legis
- ✅ Tooltip "💡 A IA do Legis procura automaticamente..."
- ✅ Botão "🔍 Buscar novas sugestões no Sigepe Legis IA"

**Coluna Direita (📚 Outras Normas):**
- ✅ Campo de busca com ícone de lupa
- ✅ Digitar texto filtra em tempo real
- ✅ Botão "✕" aparece para limpar busca
- ✅ Acordeões com 6 grupos DECIPEX
- ✅ Botão "➕ Adicionar Norma Manualmente" tracejado verde
- ✅ Campos de input manual expandem

**Rodapé Integrado (v3.0.1 FIX):**
- ✅ Dentro do container do chat (não na borda da tela)
- ✅ Borda top azul (`border-top: 3px solid #1351B4`)
- ✅ Contador "X norma(s) selecionada(s)"
- ✅ Botão "🗑️ Limpar Seleção" (se houver seleções)
- ✅ Botões "Não Sei" e "Confirmar"

### Passo 4: Testar Responsividade

**Desktop (> 968px):**
- Layout 2 colunas lado a lado

**Mobile (< 968px):**
- Layout vira 1 coluna vertical:
  1. Sugestões Helena
  2. IA Legis
  3. Busca
  4. Acordeões
  5. Adicionar Manual
  6. Rodapé

---

## 📊 Comparativo Antes/Depois

| Aspecto | Antes (v2.2) | Depois (v3.0) | Melhoria |
|---------|--------------|---------------|----------|
| Layout | Lista vertical única | 2 colunas equilibradas | ⚡ Mais espacial |
| Sugestões IA | Seção única misturada | Coluna dedicada destacada | 🎯 Mais visível |
| Busca | Nenhuma | Campo com filtro tempo real | 🔍 Mais rápido |
| IA Legis | Botão escondido | Container destacado + tooltip | 💡 Mais compreensível |
| Acordeões | Todos misturados | 6 grupos DECIPEX focados | 📚 Mais organizado |
| Mobile | Scroll infinito | Layout vertical adaptado | 📱 Melhor UX mobile |
| Rodapé | Inline no fluxo | Integrado com borda azul | ✅ Mais destacado |
| Fundo | Branco uniforme | Cinza vs Branco | 🎨 Melhor separação visual |

---

## 🎭 Experiência do Usuário

### Fluxo Ideal:

1. **Usuário chega na tela de normas**
   - 🧠 Pensamento: "Nossa, a Helena já sugeriu algumas normas pra mim!"

2. **Olha para a esquerda (Sugestões)**
   - 🧠 Pensamento: "Essas fazem sentido... vou marcar todas"
   - ✅ Clica "✓ Selecionar Todas as Sugestões"

3. **Vê o container IA Legis**
   - 🧠 Pensamento: "Ah, tem uma IA especializada em legislação!"
   - 💡 Lê tooltip: "procura automaticamente outras normas"
   - 🤔 Decisão: "Vou usar isso depois se precisar"

4. **Olha para a direita (Explorar)**
   - 🧠 Pensamento: "Hmm, será que tem mais normas relacionadas?"
   - 🔍 Digite no campo de busca: "8112"
   - ⚡ Vê filtro em tempo real mostrando Lei 8112/90 em vários grupos
   - ✅ Seleciona normas adicionais

5. **Não encontrou algo específico**
   - ➕ Clica "Adicionar Norma Manualmente"
   - ✏️ Digita: "Art. 42 da IN SGP nº 123/2023"

6. **Confirma seleção**
   - 👀 Olha rodapé: "7 norma(s) selecionada(s)"
   - ✅ Clica "Confirmar"

### Resultado:
- ✅ **Eficiente:** Encontrou normas rapidamente
- ✅ **Confiante:** IA ajudou + pôde explorar sozinho
- ✅ **Empoderado:** Adicionou norma manual quando precisou
- ✅ **Satisfeito:** Experiência fluida e sem frustrações

---

## 🧪 Casos de Teste

### Teste 1: Seleção Rápida (Usuário Confiante)
**Ação:** Clica "✓ Selecionar Todas as Sugestões" → Confirmar
**Resultado Esperado:** ✅ 3 normas selecionadas, confirmadas em < 5 segundos

### Teste 2: Busca por Keyword
**Ação:** Digite "lgpd" no campo de busca
**Resultado Esperado:** ✅ Mostra apenas Lei 13.709/2018 no grupo "Proteção de Dados"

### Teste 3: Exploração Completa
**Ação:** Abre todos os 6 acordeões, seleciona 1 norma de cada
**Resultado Esperado:** ✅ 6 normas selecionadas, contador atualiza

### Teste 4: Adicionar Manual
**Ação:** Clica "Adicionar Manualmente", digita 3 normas customizadas
**Resultado Esperado:** ✅ 3 campos visíveis, botão "➕ Adicionar Outro Campo" funciona

### Teste 5: Limpar Seleção
**Ação:** Seleciona 5 normas → Clica "🗑️ Limpar Seleção"
**Resultado Esperado:** ✅ Todas desmarcadas, contador volta para 0

### Teste 6: IA Legis
**Ação:** Clica "🔍 Buscar novas sugestões no Sigepe Legis IA"
**Resultado Esperado:** ✅ Nova aba abre para https://legis.sigepe.gov.br/legis/chat-legis

### Teste 7: Mobile Responsivo
**Ação:** Redimensiona tela para < 968px
**Resultado Esperado:** ✅ Layout vira 1 coluna vertical automático

### Teste 8: Rodapé Integrado (v3.0.1)
**Ação:** Rolar a página até o fim
**Resultado Esperado:** ✅ Rodapé aparece DENTRO do container do chat, não fixo na borda

---

## 🐛 Troubleshooting

### Problema 1: "Layout não ficou em 2 colunas"
**Causa:** Browser cache ou CSS não carregou
**Solução:**
```bash
# Rebuild frontend
cd frontend
npm run build

# Hard refresh no browser (Ctrl+Shift+R)
```

### Problema 2: "Campo de busca não filtra"
**Causa:** Estado não atualizou
**Solução:** Verifique que `categoriasFiltradas` está sendo usado no map, não `categorias`

### Problema 3: "Rodapé apareceu na borda da tela (v3.0.0 bug)"
**Causa:** CSS usava `position: fixed`
**Solução aplicada (v3.0.1):**
- Classe `.sticky-footer` → `.footer-actions`
- CSS removeu `position: fixed`
- Agora é rodapé integrado com `border-top` azul

### Problema 4: "Mobile não vira 1 coluna"
**Causa:** Media query não funciona
**Solução:** Verificar se breakpoint `@media (max-width: 968px)` está presente

---

## 📝 Changelog

### v3.0.1 (2025-10-22 - 18:19 build)
- 🐛 **FIX:** Rodapé agora é integrado ao container (não mais `position: fixed`)
- ✅ Classe renomeada: `.sticky-footer` → `.footer-actions`
- ✅ Removido `z-index: 1000` e posicionamento absoluto
- ✅ Ajustado `margin-bottom: 0` no layout 2 colunas

### v3.0.0 (2025-10-22 - 21:26 build)
- ✨ Implementação completa do layout 2 colunas
- ✨ Campo de busca com filtro em tempo real
- ✨ Botão IA Legis destacado com tooltip
- ✨ Responsividade mobile
- ✨ Fundos diferenciados (cinza vs branco)
- ❌ Bug: Rodapé fixo saía do container (corrigido em v3.0.1)

### v2.2 (anterior)
- Base legal DECIPEX com 33 normas
- 6 grupos temáticos dinâmicos do backend
- Interface vertical única

---

## 📝 Próximos Passos (Futuro)

### Melhorias de UX/UI:
- [ ] Animações de transição ao selecionar normas
- [ ] "Skeleton loading" enquanto carrega grupos do backend
- [ ] Mostrar normas recentemente selecionadas (histórico)
- [ ] Dark mode

### Melhorias de Funcionalidade:
- [ ] Salvar preferências de normas favoritas por usuário
- [ ] Integração real com API do IA Legis (buscar e importar)
- [ ] Sugerir normas complementares baseado na seleção atual
- [ ] Exportar lista de normas selecionadas (PDF/Excel)

### Melhorias de Performance:
- [ ] Virtual scroll para acordeões muito grandes
- [ ] Lazy load de grupos (carregar sob demanda)
- [ ] Cache local de últimas buscas

---

## 👥 Contribuidores

- **UX/UI Design:** Roberto (DECIPEX) - Proposta detalhada de 2 colunas
- **Implementação:** Claude Code - Layout, filtros, estilos CSS, fix rodapé
- **Data:** 2025-10-22

---

## 📚 Arquivos Relacionados

- [BASE_LEGAL_DECIPEX_V2.2.md](BASE_LEGAL_DECIPEX_V2.2.md) - Backend (33 normas + 6 grupos)
- [InterfaceNormas.tsx](../frontend/src/components/Helena/InterfaceNormas.tsx) - Componente principal (~920 linhas)
- [CLAUDE.md](../CLAUDE.md) - Instruções do projeto

---

**🎉 Layout 2 Colunas v3.0.1 - Implementado e Pronto!**

A experiência deixou de parecer "lista burocrática" e passa a se sentir como um **ambiente de descoberta**: à esquerda a IA ajuda, à direita o usuário explora. Rodapé integrado corretamente dentro do container. 🚀
