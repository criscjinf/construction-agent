# 📄 Como Enviar e Analisar Documentos

## 🚀 Opção 1: Sistema Interativo de Upload (Recomendado)

Execute o script de upload interativo:

```bash
python3 upload_documents.py
```

### Passo a Passo:

1. **Menu Principal Aparece:**
   ```
   📄 DOCUMENT UPLOAD
   
   Options:
     1. Upload CSV (bid tabulation data)
     2. Upload PDF (plans, specifications)
     3. Start analysis
     4. Quit
   ```

2. **Escolha "1" para enviar CSV:**
   ```
   👉 Choose option (1-4): 1
   ```

3. **Digite o caminho do arquivo:**
   ```
   📂 Enter file path (or 'cancel' to skip): /path/to/seu_arquivo.csv
   ```
   
   ✅ Resultado:
   ```
   ✅ File uploaded: seu_arquivo.csv (15.2KB)
   ```

4. **Envie PDFs igualmente:**
   ```
   👉 Choose option (1-4): 2
   📂 Enter file path: /path/to/plans.pdf
   ✅ File uploaded: plans.pdf (21.6MB)
   ```

5. **Inicie a análise:**
   ```
   👉 Choose option (1-4): 3
   ```

6. **Faça perguntas:**
   ```
   📍 Your question: What are the top 5 most expensive items?
   ```

---

## 📂 Opção 2: Copie Arquivos para a Pasta `data/`

### Método Rápido:

1. **Copie seus arquivos:**
   ```bash
   cp seu_arquivo.csv ~/projetos/cjl-tech/contrunction-agent/data/
   cp seu_pdf.pdf ~/projetos/cjl-tech/contrunction-agent/data/
   ```

2. **Execute o agente:**
   ```bash
   python3 test_pdf_agent.py
   # ou
   python3 run_agent.py
   ```

O sistema carrega **automaticamente** todos os CSVs e PDFs da pasta `data/`.

---

## 📊 Formatos Suportados

### CSV (Bid Tabulation Data)
- Colunas podem ter **qualquer nome**
- Sistema detecta automaticamente:
  - Item numbers, descriptions
  - Quantities, units
  - Unit prices, extended amounts
  - Bidder information

**Exemplo esperado:**
```
PROJ_ID, ITEM_NO, ITEM_DESC, UNIT, QUANTITY, UNIT_PRICE, BIDDER
P001, 1031000, MOBILIZATION, LS, 1, 33950.00, Company A
P001, 1040000, TRAFFIC CONTROL, LF, 2500, 15.50, Company A
```

### PDF (Plans & Specifications)
- ✅ PDFs com texto nativo (PyPDF2)
- ✅ PDFs scaneados (OCR automático)
- ✅ Qualquer tamanho até 100MB
- ✅ Múltiplos documentos

---

## 🎯 Exemplos de Perguntas

### Análise de CSV:
```
"What are the top 5 most expensive items?"
"Are there any pricing anomalies?"
"Compare bidder prices on MOBILIZATION"
"Items with highest price variance"
```

### Análise de PDF:
```
"What does the plan say about drainage?"
"What are the specification requirements?"
"Find information about pavement marking"
"Summarize the key project details"
```

### Buscas Semânticas:
```
"Search for asphalt items"
"Find all traffic control specifications"
"What's mentioned about utilities?"
```

---

## 💡 Dicas Importantes

### ✅ Faça:
- Use nomes descritivos de arquivos
- Envie CSVs bem-estruturados (mesmo com colunas não-padrão)
- Faça perguntas específicas

### ❌ Evite:
- Arquivos maiores que 100MB
- Formatos não suportados (use PDF ou CSV)
- Perguntas muito vagas ("analyze everything")

---

## 🔍 Fluxo de Processamento

```
Arquivo Enviado
     ↓
Validação (formato, tamanho)
     ↓
Extração de Texto (CSV parse ou PDF OCR)
     ↓
Divisão em Chunks
     ↓
Geração de Embeddings (Mock ou Real)
     ↓
Armazenamento no Vector Store
     ↓
Busca Semântica Disponível
     ↓
Claude responde suas perguntas
```

---

## 🚀 Scripts Disponíveis

| Script | Uso | Créditos |
|--------|-----|----------|
| `upload_documents.py` | Upload interativo + análise | Sim (opcional) |
| `test_interactive.py` | Local, sem upload | Não |
| `test_pdf_agent.py` | Análise de PDFs rápida | Não |
| `run_agent.py` | Análise completa | Sim |

---

## ❓ FAQ

### P: Preciso de créditos para enviar documentos?
**R:** Não! Upload e indexação são locais. Você só precisa de créditos se usar embeddings reais (não mock).

### P: Quantos documentos posso enviar?
**R:** Não há limite técnico, mas arquivos muito grandes (>100MB) podem demorar.

### P: Meu CSV tem colunas diferentes?
**R:** Sem problema! O sistema detecta automaticamente a estrutura.

### P: Posso usar PDFs escaneados?
**R:** Sim! O sistema usa OCR automático se disponível.

### P: Posso deletar documentos depois?
**R:** Sim! Cada sessão cria um banco de dados temporário que é deletado ao sair.

---

## 🔧 Solução de Problemas

### Erro: "File not found"
```
✅ Solução: Use caminho absoluto
python3 upload_documents.py
📂 Enter file path: /home/seu_usuario/Documents/arquivo.csv
```

### Erro: "Unsupported format"
```
✅ Solução: Use apenas .csv ou .pdf
❌ Não suporta: .xlsx, .txt, .doc
```

### Erro: "File too large"
```
✅ Solução: Divida em arquivos menores ou use dados essenciais
❌ Limite: 100MB por arquivo
```

---

**Pronto para enviar documentos?** 🚀

```bash
python3 upload_documents.py
```
