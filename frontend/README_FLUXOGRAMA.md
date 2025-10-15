# Gerador de Fluxogramas - React Migration

## 📋 Visão Geral

Página do **Gerador de Fluxogramas** migrada de HTML vanilla para **React 19 + TypeScript**.

### ✅ Funcionalidades Implementadas

1. **Upload de PDF com Drag & Drop**
   - Suporte a arrastar e soltar arquivos PDF
   - Validação de tipo e tamanho (máx. 10MB)
   - Feedback visual durante upload
   - Barra de progresso

2. **Chat Conversacional com Helena**
   - Interface de chat integrada
   - Animação de "digitando..." durante respostas
   - Auto-scroll para última mensagem
   - Habilitado apenas após análise do PDF

3. **Visualização de Fluxograma com Mermaid**
   - Renderização dinâmica de fluxogramas
   - Suporte a código Mermaid
   - Ações disponíveis:
     - 📥 Baixar SVG
     - 📋 Copiar código Mermaid
     - 🖨️ Imprimir fluxograma

4. **Responsividade**
   - Layout adaptativo para mobile e desktop
   - Grid responsivo (2 colunas → 1 coluna em mobile)

## 📁 Estrutura de Arquivos

```
frontend/src/
├── pages/
│   ├── FluxogramaPage.tsx          # Página principal
│   └── FluxogramaPage.css          # Estilos da página
├── components/
│   └── Fluxograma/
│       ├── FluxogramaUpload.tsx    # Componente de upload
│       ├── FluxogramaUpload.css
│       ├── FluxogramaChat.tsx      # Componente de chat
│       ├── FluxogramaChat.css
│       ├── FluxogramaPreview.tsx   # Visualizador Mermaid
│       └── FluxogramaPreview.css
├── App.tsx                         # Rota adicionada
└── data/
    └── products.ts                 # Status atualizado para "Disponível"
```

## 🔌 Integração com Backend

### API Endpoints Utilizados

**POST `/api/fluxograma-from-pdf/`**

**Fase 1: Upload de PDF**
```typescript
// Request
FormData {
  pdf_file: File
}

// Response
{
  success: boolean,
  pop_info: {
    atividade?: string,
    objetivo?: string,
    operadores?: string[],
    sistemas?: string[],
    etapas?: string[],
    documentos?: string[]
  },
  message: string,
  file_name: string
}
```

**Fase 2: Conversa com Helena**
```typescript
// Request
{
  message: string
}

// Response
{
  resposta: string,
  conversa_completa: boolean,
  dados_extraidos?: object,
  progresso?: string
}
```

### Backend Files

- **View:** `processos/views.py::fluxograma_from_pdf`
- **Produto Helena:** `processos/helena_produtos/helena_fluxograma.py`

## 🚀 Como Usar

1. **Acessar a página:**
   ```
   http://localhost:5174/fluxograma
   ```

2. **Upload do PDF:**
   - Clique ou arraste um PDF de POP para a área de upload
   - Aguarde a análise (barra de progresso)

3. **Conversar com Helena:**
   - Após análise, o chat é habilitado
   - Helena faz perguntas sobre o processo
   - Responda para mapear etapas, decisões, responsáveis

4. **Visualizar Fluxograma:**
   - Quando a conversa estiver completa, o fluxograma é gerado
   - Baixe como SVG, copie o código ou imprima

## 🎨 Design

- **Paleta de cores:** Gradiente roxo (#667eea → #764ba2)
- **Tipografia:** Segoe UI, sans-serif
- **Ícones:** Emojis nativos
- **Animações:** Fade-in, typing indicator, hover effects

## 📦 Dependências

```json
{
  "mermaid": "^10.x"  // Para renderização de fluxogramas
}
```

## ⚙️ Configuração

### Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🔄 Migração do HTML

### Arquivo Antigo
- **Localização:** `processos/templates/fluxograma.html` → `fluxograma.html.bak`
- **Status:** Desativado (rota comentada em `processos/urls.py`)

### Melhorias em Relação ao HTML Antigo

1. **Componentização:** Código modular e reutilizável
2. **Type Safety:** TypeScript previne erros
3. **State Management:** React hooks para estado consistente
4. **Performance:** Re-renderização otimizada
5. **Developer Experience:** Hot reload, debugging avançado
6. **Manutenibilidade:** Código mais limpo e organizado

## 🐛 Debugging

### Verificar se Mermaid está instalado
```bash
cd frontend
npm list mermaid
```

### Testar API manualmente
```bash
curl -X POST http://localhost:8000/api/fluxograma-from-pdf/ \
  -F "pdf_file=@seu_arquivo.pdf"
```

### Logs do Frontend
Abra o Console do navegador (F12) para ver logs de requisições e erros.

## 📝 Próximos Passos

- [ ] Integrar com sistema de salvamento de fluxogramas
- [ ] Permitir edição manual do código Mermaid
- [ ] Suporte a exportação em PNG/JPG
- [ ] Histórico de fluxogramas gerados
- [ ] Templates de fluxogramas pré-definidos

## 🤝 Contribuindo

Para adicionar novos recursos:

1. Crie componentes em `components/Fluxograma/`
2. Mantenha estilos em arquivos `.css` separados
3. Siga a estrutura de pastas existente
4. Documente mudanças neste README

---

**Última atualização:** 14 de outubro de 2025
**Autor:** Migração HTML → React
