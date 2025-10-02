# MapaGov 🇧🇷

Sistema de Governança, Riscos e Conformidade (GRC) para o setor público brasileiro.

## 🌐 Idioma

**Esta aplicação está 100% em Português Brasileiro (pt-BR)**

O MapaGov foi desenvolvido especificamente para o contexto brasileiro, utilizando:
- ✅ Interface completamente em Português do Brasil
- ✅ Terminologia técnica adequada ao setor público brasileiro
- ✅ Conformidade com normas e regulamentos nacionais
- ✅ Fuso horário: America/São Paulo
- ✅ Assistente virtual Helena que se comunica em português natural

## 📋 Sobre o Projeto

MapaGov é uma plataforma integrada para auxiliar órgãos públicos no mapeamento de processos, análise de riscos e conformidade regulatória, com foco em:

- **Mapeamento de Processos**: Criação de POPs (Procedimentos Operacionais Padrão)
- **Análise de Riscos**: Identificação e avaliação de riscos nos processos
- **Conformidade**: Verificação de aderência às normas e regulamentos
- **Governança**: Gestão integrada de processos e documentação

## 🤖 Helena - Assistente Inteligente

Helena é a assistente virtual do MapaGov, especializada em:
- Mapeamento de processos da DECIPEX
- Análise de base legal
- Orientação sobre normas e regulamentos
- Geração de documentação estruturada

**Helena fala Português Brasileiro de forma natural e contextualizada.**

## ⚙️ Configuração de Idioma

A aplicação está configurada para operar em Português do Brasil através das seguintes configurações:

### Django Settings (`mapagov/settings.py`)
```python
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
```

### Templates HTML
Todos os templates incluem:
```html
<html lang="pt-br">
```

## 🚀 Como Executar

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente (`.env`):
   ```
   SECRET_KEY=sua-chave-secreta
   DEBUG=True
   ```

4. Execute as migrações:
   ```bash
   python manage.py migrate
   ```

5. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

6. Acesse: `http://localhost:8000`

## 📚 Recursos em Português

- **Documentação**: Toda documentação em português
- **Mensagens de erro**: Traduzidas e contextualizadas
- **Interface do usuário**: Botões, labels e instruções em PT-BR
- **Base legal**: Referências a normas brasileiras (Lei 8.112/90, etc.)
- **Terminologia**: Adequada ao contexto da administração pública federal

## 🎯 Produtos Disponíveis

1. **P1: Gerador de POP** ✅ Disponível
2. **P2: Fluxograma** 🔨 Em Desenvolvimento
3. **P3: Dossiê PDF** 📋 Planejado
4. **P4: Dashboard** 📋 Planejado
5. **P5: Análise de Riscos** ✅ Disponível
6. **P6: Relatório Riscos** 📋 Planejado
7. **P7: Plano de Ação** 📋 Planejado
8. **P8: Dossiê Governança** 📋 Planejado

## 📞 Contato

Para dúvidas ou suporte, utilize a interface de chat com Helena ou entre em contato com a equipe de desenvolvimento.

---

**Sim, nós falamos Português do Brasil! 🇧🇷**
