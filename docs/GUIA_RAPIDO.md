# 🚀 GUIA RÁPIDO - Run Agent Unificado

## ✨ Visão Geral

Agora existe **um único comando** que faz TUDO:

```bash
python3 run_agent.py
```

Este script oferece 3 opções:
1. **Upload novo** - Enviar CSVs e PDFs
2. **Load from data/** - Usar arquivos já na pasta
3. **Ambos** - Upload + dados existentes

Depois indexa tudo e você faz perguntas.

---

## 🎯 Fluxo Completo em 3 Passos

### Passo 1: Execute o comando
```bash
python3 run_agent.py
```

### Passo 2: Escolha como carregar documentos
```
👉 Choose (1-3): 2
```
(Seleciona "Load from data/" - mais rápido)

### Passo 3: Faça perguntas
```
📍 You: What are the top 5 most expensive items?

🤖 Claude is analyzing...
---------
Top 5 most expensive items...
---------
```

---

## 📋 Opções de Carregamento

### **Opção 1: Upload Novo**
```
👉 Choose (1-3): 1

🚀 UPLOAD MODE
👉 Choose (1-3): 1
📂 Enter file path: /path/to/seu_arquivo.csv
✅ Uploaded: seu_arquivo.csv (15.2KB)

👉 Choose (1-3): 2
📂 Enter file path: /path/to/seu_pdf.pdf
✅ Uploaded: seu_pdf.pdf (21.6MB)

👉 Choose (1-3): 3
[Começa análise]
```

### **Opção 2: Usar data/ (RECOMENDADO)**
```
👉 Choose (1-3): 2

✅ Loaded 1 documents
[Automaticamente carrega CSV + PDFs da pasta data/]
```

### **Opção 3: Upload + data/**
```
👉 Choose (1-3): 3

[Você faz upload + carrega o que já existe em data/]
```

---

## 💬 Exemplo Completo

```bash
$ python3 run_agent.py

==========================================================================================
  🤖 CONSTRUCTION ESTIMATING AGENT
==========================================================================================

==========================================================================================
  📄 DOCUMENT LOADING
==========================================================================================

Options:
  1. Upload new documents (CSV/PDF)
  2. Load from data/ folder
  3. Both (upload + load from data/)

👉 Choose (1-3): 2

✅ Documents ready for indexing: 4

==========================================================================================
  📊 INDEXING DOCUMENTS
==========================================================================================

Loading CSV: data/sample_bid_tabulation.csv
✅ Indexing complete:
   • CSV items: 120
   • PDF chunks: 1847
   • Total: 1967

==========================================================================================
  🤖 INITIALIZING AGENT
==========================================================================================

✅ Agent ready with 4 tools
   • Search (CSV + PDF)
   • Top Items
   • Outlier Detection
   • Bidder Comparison

==========================================================================================
  💬 ANALYSIS MODE
==========================================================================================

💡 Ask questions about your documents!

Examples:
  • "What are the top 5 most expensive items?"
  • "What does the plan say about drainage?"
  • "Are there pricing anomalies?"
  • "Find information about..."

Commands: 'help', 'examples', 'quit'
==========================================================================================

📍 You: What are the top 5 most expensive items?

🤖 Claude is analyzing...

------------------------------------------------------------------------------------------
Here are the **Top 5 Most Expensive Bid Items**:

1. MOBILIZATION - $33,950.00
2. MOBILIZATION - $26,500.00
3. EVALUATION OF PAVEMENT MARKING - $35,000.00
...
------------------------------------------------------------------------------------------

📍 You: What about drainage in the plan?

🤖 Claude is analyzing...

------------------------------------------------------------------------------------------
Based on the plan documents, the drainage system includes:
- Underdrains installation
- Storm water management
...
------------------------------------------------------------------------------------------

📍 You: quit

👋 Goodbye!
```

---

## ⚡ Atalhos Úteis

Dentro do programa, você pode usar:

| Comando | O que faz |
|---------|-----------|
| `help` | Mostra ajuda |
| `examples` | Lista exemplos de perguntas |
| `quit` | Sai do programa |

---

## 🎯 Casos de Uso

### Cenário 1: Análise Rápida
```bash
# Arquivos já estão em data/
python3 run_agent.py
# Escolha: 2
# Faça perguntas
```

### Cenário 2: Novos Dados
```bash
# Tem novo CSV/PDF para analisar
python3 run_agent.py
# Escolha: 1
# Faça upload
# Faça perguntas
```

### Cenário 3: Dados Múltiplos
```bash
# Quer usar dados de data/ + novos uploads
python3 run_agent.py
# Escolha: 3
# Faça uploads
# Faça perguntas
```

---

## ❓ FAQ Rápido

**P: Preciso de múltiplos comandos?**
R: Não! Um único `python3 run_agent.py`

**P: Posso mudar de documentos sem sair?**
R: Não. Saia com `quit` e execute novamente.

**P: Onde coloco meus arquivos?**
R: 
- Opção A: Na pasta `data/` 
- Opção B: Qualquer lugar, e faça upload

**P: Os dados são salvos?**
R: Não. Cada sessão cria banco temporário que é deletado ao sair.

**P: Quantos documentos posso usar?**
R: Sem limite técnico (até 100MB cada)

---

## 🔧 Estrutura de Pastas

```
projeto/
├── run_agent.py          ← Use este! (único comando)
├── data/
│   ├── sample_bid_tabulation.csv
│   ├── plans.pdf
│   ├── specifications-vol-1.pdf
│   └── specifications-vol-2.pdf
├── src/
│   ├── data/
│   │   ├── loaders.py
│   │   ├── parsers.py
│   │   ├── pdf_parser.py
│   │   └── document_loader.py  ← Faz o upload/indexação
│   ├── agent/
│   │   └── core.py
│   ├── vectorstore/
│   │   └── storage.py
│   └── analysis/
```

---

## 🚀 TL;DR - Comece Agora!

```bash
python3 run_agent.py
# Escolha: 2
# Digite: What are the top items?
# Done!
```

**Um único comando para fazer TUDO.** ✅
