# 📋 Exemplos de Logs - Entenda cada mensagem

## 1️⃣ Inicialização Normal (LOG_LEVEL=INFO)

```
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

✅ Documents ready for indexing: 1

==========================================================================================
  📊 INDEXING DOCUMENTS
==========================================================================================

Loading CSV: data/sample_bid_tabulation.csv
✅ Indexing complete:
   • CSV items: 120
   • PDF chunks: 0
   • Total: 120
```

**Análise:**
- ✅ Documentos carregados
- ✅ CSV indexado corretamente
- ✅ Nenhum PDF encontrado (normal)

---

## 2️⃣ Inicialização com LOG_LEVEL=DEBUG

```
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | ================================================================================
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | Starting Construction Agent | Debug Mode: True
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | Config: DEBUG=true, LOG_FILE=logs/construction_agent.log
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | ================================================================================

2026-05-08 14:32:45 | INFO    | run_agent            | main                 | 📄 Starting document loading process...
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | Document loading complete: 1 files, 1 projects

2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | Created temporary database: /tmp/tmp123abc.db
2026-05-08 14:32:45 | INFO    | run_agent            | main                 | 📊 Initializing SQLite vector store at /tmp/tmp123abc.db
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | ✅ Vector store initialized

2026-05-08 14:32:45 | INFO    | run_agent            | main                 | 📦 Initializing DocumentLoader with mock embeddings
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | ✅ DocumentLoader initialized

2026-05-08 14:32:46 | INFO    | run_agent            | main                 | 📄 Starting indexing of 1 documents...
2026-05-08 14:32:46 | DEBUG   | run_agent            | main                 | 🔄 Indexing CSV: sample_bid_tabulation.csv
2026-05-08 14:32:46 | INFO    | document_loader      | load_and_index_csv   | Loading CSV: data/sample_bid_tabulation.csv
2026-05-08 14:32:46 | DEBUG   | loaders              | load                 | Loading data/sample_bid_tabulation.csv with CSVParser
2026-05-08 14:32:46 | DEBUG   | parsers              | parse                | Inferring schema from CSV (first 5 rows)...
2026-05-08 14:32:47 | INFO    | document_loader      | load_and_index_csv   | Indexed 120 bid items from CSV
2026-05-08 14:32:47 | INFO    | run_agent            | main                 | ✅ CSV indexed: sample_bid_tabulation.csv (120 items)

2026-05-08 14:32:47 | INFO    | run_agent            | main                 | ✅ Indexing complete: CSV=120, PDF=0
2026-05-08 14:32:47 | INFO    | run_agent            | main                 | 🤖 Initializing Claude agent...
2026-05-08 14:32:47 | DEBUG   | run_agent            | main                 | AgentExecutor initializing with 1 projects and vector_store
2026-05-08 14:32:47 | INFO    | agent.core           | __init__             | Initializing AgentExecutor...
2026-05-08 14:32:47 | DEBUG   | agent.core           | __init__             | ANTHROPIC_API_KEY loaded from environment
2026-05-08 14:32:47 | DEBUG   | agent.core           | __init__             | Creating Anthropic client with API key
2026-05-08 14:32:47 | INFO    | agent.core           | __init__             | ✅ Agent ready with 4 tools
2026-05-08 14:32:47 | INFO    | run_agent            | main                 | ✅ Agent ready with 4 tools
```

**O que vemos:**
1. 🔧 **Inicialização**: Toda configuração foi carregada corretamente
2. 📂 **Documentos**: CSV foi encontrado e carregado
3. 📊 **Indexação**: 120 items foram indexados no vector store
4. 🤖 **Agente**: API key detectada, Anthropic client criado
5. ✅ **Pronto**: 4 tools estão disponíveis

---

## 3️⃣ Query Bem-Sucedida (LOG_LEVEL=DEBUG)

```
📍 You: What are the top 3 items?

2026-05-08 14:32:50 | INFO    | run_agent            | main                 | 📍 User query: What are the top 3 items?
2026-05-08 14:32:50 | DEBUG   | run_agent            | main                 | 🔄 Executing agent.query() for: What are the top 3 items?
2026-05-08 14:32:50 | INFO    | run_agent            | main                 | 🔧 Agent processing query...

2026-05-08 14:32:50 | DEBUG   | agent.core           | query                | Entering agent loop (iteration 1/5)
2026-05-08 14:32:50 | DEBUG   | agent.core           | query                | Calling Claude API with 4 tools...
2026-05-08 14:32:52 | DEBUG   | agent.core           | query                | Claude response stop_reason: tool_use
2026-05-08 14:32:52 | DEBUG   | agent.core           | query                | Detected tool call: aggregate_items
2026-05-08 14:32:52 | DEBUG   | agent.core           | _execute_tool        | Executing tool: aggregate_items
2026-05-08 14:32:52 | DEBUG   | agent.core           | _tool_aggregate_items | Fetching top items by unit_price

2026-05-08 14:32:52 | DEBUG   | analysis.aggregations| get_top_items        | Sorting 120 items by unit_price (desc)
2026-05-08 14:32:52 | DEBUG   | analysis.aggregations| get_top_items        | Found 120 items, returning top 3
2026-05-08 14:32:52 | DEBUG   | agent.core           | _tool_aggregate_items | Got 3 results

2026-05-08 14:32:52 | DEBUG   | agent.core           | query                | Tool result: "Top 3 highest items by unit price: ..."
2026-05-08 14:32:52 | DEBUG   | agent.core           | query                | Entering agent loop (iteration 2/5)
2026-05-08 14:32:52 | DEBUG   | agent.core           | query                | Calling Claude API...
2026-05-08 14:32:54 | DEBUG   | agent.core           | query                | Claude response stop_reason: end_turn
2026-05-08 14:32:54 | DEBUG   | agent.core           | query                | Agent finished (end_turn)

2026-05-08 14:32:54 | INFO    | run_agent            | main                 | ✅ Agent returned response
2026-05-08 14:32:54 | DEBUG   | run_agent            | main                 | Response length: 456 characters

🤖 Claude is analyzing...

------------------------------------------------------------------------------------------
Here are the **Top 3 Most Expensive Bid Items**:

1. MOBILIZATION - $33,950.00
2. EVALUATION OF PAVEMENT MARKING - $35,000.00
3. TRAFFIC CONTROL - $31,200.00
------------------------------------------------------------------------------------------
```

**Entendendo o Fluxo:**
1. Query recebida → Logs de entrada
2. Agent loop iteração 1 → Claude chamado
3. Tool call detectado → `aggregate_items` acionada
4. Função executada → 3 items retornados
5. Agent loop iteração 2 → Claude processa resultado
6. `end_turn` → Agent concluiu
7. Resposta → 456 caracteres

---

## 4️⃣ Erro em Upload de Arquivo (LOG_LEVEL=DEBUG)

```
2026-05-08 14:35:12 | INFO    | run_agent            | load_documents       | 📄 Document loading starting...
2026-05-08 14:35:12 | DEBUG   | run_agent            | upload_file          | User attempting file upload...

2026-05-08 14:35:15 | DEBUG   | run_agent            | upload_file          | File path provided: /tmp/corrupted.pdf
2026-05-08 14:35:15 | DEBUG   | run_agent            | upload_file          | File exists: True, Size: 45.2MB

2026-05-08 14:35:15 | DEBUG   | run_agent            | upload_file          | File type: .pdf, Destination: /tmp/construction_agent_xyz/corrupted.pdf
2026-05-08 14:35:15 | DEBUG   | run_agent            | upload_file          | Copying file...
2026-05-08 14:35:16 | INFO    | run_agent            | upload_file          | ✅ Uploaded: corrupted.pdf (45.2MB)

2026-05-08 14:35:16 | DEBUG   | run_agent            | main                 | 🔄 Indexing PDF: corrupted.pdf
2026-05-08 14:35:16 | DEBUG   | document_loader      | load_and_index_pdf   | Loading PDF: /tmp/construction_agent_xyz/corrupted.pdf
2026-05-08 14:35:16 | DEBUG   | pdf_parser           | _extract_text        | Starting PDF text extraction...
2026-05-08 14:35:16 | DEBUG   | pdf_parser           | _extract_text        | Attempting PyPDF2 extraction...

2026-05-08 14:35:18 | WARNING | pdf_parser           | _extract_text        | PyPDF2 extraction failed: Could not get pages. The PDF may be corrupted.
2026-05-08 14:35:18 | DEBUG   | pdf_parser           | _extract_text        | Fallback: Trying OCR extraction...
2026-05-08 14:35:18 | DEBUG   | pdf_parser           | _extract_with_ocr    | Checking OCR availability...

2026-05-08 14:35:19 | WARNING | pdf_parser           | _extract_with_ocr    | pytesseract not installed or tesseract binary not found
2026-05-08 14:35:19 | DEBUG   | pdf_parser           | _extract_text        | OCR fallback failed

2026-05-08 14:35:19 | ERROR   | document_loader      | load_and_index_pdf   | Failed to load PDF: /tmp/construction_agent_xyz/corrupted.pdf - No text extracted
2026-05-08 14:35:19 | WARNING | run_agent            | main                 | ⚠️  Error indexing corrupted.pdf: Failed to load PDF - No text extracted

✅ Uploaded: corrupted.pdf (45.2MB)

==========================================================================================
  📊 INDEXING DOCUMENTS
==========================================================================================

✅ Indexing complete:
   • CSV items: 120
   • PDF chunks: 0
   • Total: 120
```

**Análise do Erro:**
1. ✅ Upload foi bem-sucedido
2. ⚠️ PyPDF2 falhou → PDF pode estar corrompido
3. ⚠️ OCR não disponível → Sem fallback
4. ❌ 0 chunks indexados do PDF
5. Sistema continuou com CSV (graceful degradation)

---

## 5️⃣ Erro em Query (LOG_LEVEL=DEBUG)

```
📍 You: Compare prices on INVALIDITEM

2026-05-08 14:37:30 | INFO    | run_agent            | main                 | 📍 User query: Compare prices on INVALIDITEM
2026-05-08 14:37:30 | DEBUG   | run_agent            | main                 | 🔄 Executing agent.query() for: Compare prices on INVALIDITEM
2026-05-08 14:37:30 | INFO    | run_agent            | main                 | 🔧 Agent processing query...

2026-05-08 14:37:30 | DEBUG   | agent.core           | query                | Entering agent loop (iteration 1/5)
2026-05-08 14:37:30 | DEBUG   | agent.core           | query                | Calling Claude API with 4 tools...
2026-05-08 14:37:32 | DEBUG   | agent.core           | query                | Claude response stop_reason: tool_use
2026-05-08 14:37:32 | DEBUG   | agent.core           | query                | Detected tool call: compare_bidders
2026-05-08 14:37:32 | DEBUG   | agent.core           | _execute_tool        | Executing tool: compare_bidders
2026-05-08 14:37:32 | DEBUG   | agent.core           | _tool_compare_bidders| Looking for item: INVALIDITEM

2026-05-08 14:37:32 | DEBUG   | analysis.comparisons | compare_bidders_on_item | Searching in 1 projects for item: INVALIDITEM
2026-05-08 14:37:32 | WARNING | analysis.comparisons | compare_bidders_on_item | Item INVALIDITEM not found
2026-05-08 14:37:32 | DEBUG   | agent.core           | _tool_compare_bidders| No comparisons found, returning not found message

2026-05-08 14:37:32 | DEBUG   | agent.core           | query                | Tool result: "Item INVALIDITEM not found..."
2026-05-08 14:37:32 | DEBUG   | agent.core           | query                | Entering agent loop (iteration 2/5)
2026-05-08 14:37:33 | DEBUG   | agent.core           | query                | Calling Claude API...
2026-05-08 14:37:34 | DEBUG   | agent.core           | query                | Claude response stop_reason: end_turn
2026-05-08 14:37:34 | DEBUG   | agent.core           | query                | Agent finished

2026-05-08 14:37:34 | INFO    | run_agent            | main                 | ✅ Agent returned response
2026-05-08 14:37:34 | DEBUG   | run_agent            | main                 | Response length: 187 characters

🤖 Claude is analyzing...

------------------------------------------------------------------------------------------
I couldn't find an item with that name. Could you provide the item number or a more specific description?
------------------------------------------------------------------------------------------
```

**Análise:**
1. ✅ Query processada
2. 🔍 Tool executada corretamente
3. ⚠️ Item não encontrado (esperado)
4. ✅ Agent retornou resposta apropriada (sem erro)

---

## 📊 Resumo de Padrões

### Sucesso:
```
INFO | Operation started
DEBUG | Details of operation
DEBUG | Sub-operations
INFO | Operation complete ✅
```

### Aviso:
```
INFO | Operation started
WARNING | Something unexpected but recoverable
DEBUG | Fallback mechanism
INFO | Operation completed with limitations ⚠️
```

### Erro:
```
INFO | Operation started
ERROR | Critical failure
DEBUG | Exception details
WARNING | System continuing despite error
```

---

## 🎯 Como Ler Logs

1. **Procure por timestamps:** Mostram ordem de execução
2. **Procure por símbolos:** ✅ = sucesso, ⚠️ = aviso, ❌ = erro
3. **Procure por função:** Mostra qual código está rodando
4. **Procure por mensagens:** Explicam o que está acontecendo

---

**Agora você consegue entender qualquer problema pelo log!** 🔍
