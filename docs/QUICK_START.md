# 🚀 Quick Start - Construction Estimating Agent

## ⚡ TL;DR (30 segundos)

```bash
python3 scripts/run_agent.py
# → Escolha opção 2 (load from data/)
# → Faça perguntas
```

---

## 📋 Visão Geral

O agente oferece **um único comando** que faz tudo:
- ✅ Upload de CSV/PDF
- ✅ Indexação automática (embeddings)
- ✅ Pesquisa semântica
- ✅ Análise com Claude

---

## 🎯 Fluxo Completo

### **Opção 1: Usar dados já em `data/` (RECOMENDADO)**

```bash
python3 scripts/run_agent.py
```

Menu:
```
👉 Choose (1-3): 2
```

Resultado:
```
✅ Documents ready for indexing: 4
📊 Indexing...
✅ Agent ready with 4 tools
```

### **Opção 2: Fazer upload de novos arquivos**

```bash
python3 scripts/run_agent.py
```

Menu:
```
👉 Choose (1-3): 1

🚀 UPLOAD MODE
Options:
  1. Upload a file (auto-detect CSV/PDF)
  2. Start analysis

👉 Choose (1-2): 1
📂 Enter file path: /path/to/seu_arquivo.csv
✅ Uploaded: seu_arquivo.csv
   Detected type: CSV
   ✅ CSV parsed: 2 projects

👉 Choose (1-2): 2
```

### **Opção 3: Upload + dados existentes**

```bash
python3 scripts/run_agent.py
```

Menu:
```
👉 Choose (1-3): 3
[Faz upload E carrega data/ simultaneamente]
```

---

## 💬 Fazendo Perguntas

Após escolher opção, você conversa assim:

```
📍 You: What are the top 5 most expensive items?

🤖 Claude is analyzing...

------------------------------------------------------------------------------------------
Here are the **Top 5 Most Expensive Bid Items**:

1. MOBILIZATION - $33,950.00
2. EVALUATION OF PAVEMENT MARKING - $35,000.00
3. TRAFFIC CONTROL - $28,400.00
...
------------------------------------------------------------------------------------------

📍 You: What about drainage in the plan?

🤖 Claude is analyzing...

------------------------------------------------------------------------------------------
Based on the plan documents, the drainage system includes:
- Underdrains installation
- Storm water management
- Pipe specifications...
------------------------------------------------------------------------------------------

📍 You: quit

👋 Goodbye!
```

---

## 📊 Formatos Suportados

### CSV (Bid Tabulation)
- ✅ Qualquer estrutura de coluna
- ✅ Nomes podem variar (UNIT_PRICE, unit_price, estimate_price, etc)
- ✅ Campos vazios são tolerados
- ✅ Múltiplos projetos em um arquivo

**Exemplo esperado:**
```
PROJ_ID, ITEM_NO, ITEM_DESC, QUANTITY, UNIT_PRICE, BIDDER
P001, 1031000, MOBILIZATION, 1, 33950.00, Company A
P001, 1040000, TRAFFIC CONTROL, 2500, 15.50, Company A
```

### PDF (Plans & Specifications)
- ✅ PDFs com texto nativo (PyPDF2)
- ✅ PDFs scaneados com OCR
- ✅ Até 100MB por arquivo
- ✅ Múltiplos documentos
- ✅ Qualquer conteúdo (drawings, tables, text)

---

## 🎯 Exemplos de Perguntas

### Análise de CSV:
```
"What are the top 5 most expensive items?"
"Are there any pricing anomalies?"
"Compare bidder prices on MOBILIZATION"
"Which items have highest price variance?"
"Items with the most bidder competition"
```

### Análise de PDF:
```
"What does the plan say about drainage?"
"What are the specification requirements?"
"Find information about pavement marking"
"Summarize the key project details"
"What utilities are mentioned?"
```

### Buscas Semânticas:
```
"Search for asphalt items"
"Find all traffic control specifications"
"What's mentioned about excavation?"
```

---

## ⚡ Atalhos dentro do programa

| Comando | Efeito |
|---------|--------|
| `help` | Mostra ajuda e exemplos |
| `examples` | Lista perguntas sugeridas |
| `quit` | Sai do programa |

---

## 🚀 Scripts Disponíveis

| Script | Uso | Quando Usar |
|--------|-----|------------|
| **`scripts/run_agent.py`** | Upload + indexação + análise | **Sempre! É o principal** |
| `scripts/demo.py` | Demo automática (sem upload) | Teste rápido, sem interação |

---

## 📁 Organização de Arquivos

```
projeto/
├── scripts/
│   ├── run_agent.py     ⭐ Use este!
│   └── demo.py          (demo automática)
├── data/                (seus CSVs e PDFs aqui)
│   ├── sample_bid_tabulation.csv
│   ├── plans.pdf
│   └── ...
├── src/
│   ├── data/            (parsers, loaders)
│   ├── vectorstore/     (embeddings, storage)
│   ├── agent/           (Claude tool-use)
│   └── analysis/        (outliers, comparisons)
└── tests/               (130+ tests)
    ├── unit/
    └── integration/
```

---

## ❓ FAQ

**P: Preciso de créditos para usar?**
R: Não obrigatório. Upload/indexação são locais. Créditos só são necessários se usar embeddings reais (não mock).

**P: Meus dados são salvos?**
R: Não. Cada sessão usa banco temporário deletado ao sair. Para persistência, copie arquivos para `data/`.

**P: Quantos documentos posso usar?**
R: Sem limite técnico (até 100MB cada arquivo).

**P: Meu CSV tem estrutura diferente?**
R: Sem problema! Sistema detecta automaticamente colunas.

**P: Posso usar PDFs escaneados?**
R: Sim! OCR automático é aplicado.

**P: Como adiciono dados permanentemente?**
R: Copie CSVs/PDFs para a pasta `data/` e carregue com opção 2 ou 3.

---

## 🔧 Solução de Problemas

### Erro: "File not found"
```bash
# Use caminho absoluto
python3 scripts/run_agent.py
📂 Enter file path: /home/seu_usuario/Documents/arquivo.csv
```

### Erro: "Invalid format"
```
❌ Recebido: .xlsx, .txt, .doc
✅ Suportado: .csv, .pdf
```

### Erro: "File too large"
```
Limite: 100MB por arquivo
Solução: Divida em arquivos menores
```

### API Credits Exhausted
```
Se usar embeddings reais e os créditos acabarem:
✅ Sistema detecta e usa mock embeddings automaticamente
✅ Busca continua funcionando (menos precisa)
```

---

## 🎬 Próximos Passos

1. **Primeiro uso:**
   ```bash
   cp .env.example .env
   # (adicione suas API keys se quiser embeddings reais)
   python3 scripts/run_agent.py
   # Escolha: 2
   ```

2. **Com seus dados:**
   ```bash
   cp seu_arquivo.csv data/
   python3 scripts/run_agent.py
   # Escolha: 2
   ```

3. **Fazer upload sem salvar:**
   ```bash
   python3 scripts/run_agent.py
   # Escolha: 1
   ```

---

## 📚 Documentação Adicional

- `DEBUGGING.md` — Ativar logs detalhados
- `EMBEDDINGS.md` — Como funcionam embeddings e busca
- `SECURITY.md` — Auditoria de segurança
- `EXAMPLES.md` — Saídas e logs detalhados

---

**Pronto para começar?**
```bash
python3 scripts/run_agent.py
```
