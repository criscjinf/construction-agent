# 🧠 Como Funcionam os Embeddings - CSV vs PDF

## 📊 CSV - Item por Item

### Fluxo:

```
CSV (sample_bid_tabulation.csv)
        ↓
   Parser (detecta colunas)
        ↓
   Para cada item:
   ┌─────────────────────────────────────┐
   │ Item #1031000                       │
   │ "MOBILIZATION - LS @ $33950.00"     │
   │                                      │
   │ ↓ EMBEDDING (OpenAI)                │
   │                                      │
   │ [0.234, -0.156, 0.789, ...]        │
   │ (1536 dimensões)                    │
   │                                      │
   │ ↓ Armazena em Vector Store          │
   │ doc_id: csv_proj1_1031000           │
   └─────────────────────────────────────┘

   ┌─────────────────────────────────────┐
   │ Item #1040000                       │
   │ "TRAFFIC CONTROL - LF @ $15.50"     │
   │        ↓ EMBEDDING → [...]          │
   │ doc_id: csv_proj1_1040000           │
   └─────────────────────────────────────┘
   
   ... (120 items total)
```

### Resultado:
- ✅ **120 documentos** indexados
- ✅ Cada item é uma **string curta**
- ✅ Cada string tem um **embedding** separado
- ✅ Busca semântica funciona em items individuais

---

## 📄 PDF - Dividido em Chunks

### Fluxo:

```
PDF (plans.pdf - 21.6MB)
        ↓
   Extração de Texto (PyPDF2 ou OCR)
   Result: 193,846 caracteres
        ↓
   Divisão em Chunks (tamanho ~500 chars)
        ↓
   Para cada chunk:
   ┌──────────────────────────────────────┐
   │ Chunk #0                             │
   │ "MoDOT PROJECT NO. 21-082A-3...     │
   │ NEVADA MUNICIPAL AIRPORT (NVD)...   │
   │ Base Bid Reconstruct Runway..."     │
   │                                       │
   │ ↓ EMBEDDING (OpenAI)                 │
   │                                       │
   │ [0.512, -0.234, 0.101, ...]         │
   │ (1536 dimensões)                     │
   │                                       │
   │ ↓ Armazena em Vector Store           │
   │ doc_id: pdf_plans_chunk_0            │
   └──────────────────────────────────────┘

   ┌──────────────────────────────────────┐
   │ Chunk #1                             │
   │ "Installation of underdrains...     │
   │ Storm water management..."          │
   │        ↓ EMBEDDING → [...]          │
   │ doc_id: pdf_plans_chunk_1            │
   └──────────────────────────────────────┘
   
   ... (1847 chunks total)
```

### Resultado:
- ✅ **~1847 chunks** indexados
- ✅ Cada chunk é um **bloco de texto** (~500 caracteres)
- ✅ Cada chunk tem um **embedding** separado
- ✅ Busca semântica funciona em partes do documento

---

## 🔍 Diferenças Chave

| Aspecto | CSV | PDF |
|---------|-----|-----|
| **O que é embedado** | Cada item (descrição + preço) | Chunks de texto (parágrafos) |
| **Número de documentos** | Poucos (120 items) | Muitos (1000+) |
| **Tamanho de cada doc** | Pequeno (50-100 chars) | Médio (500 chars) |
| **Estrutura** | Estruturada (colunas) | Não-estruturada (texto livre) |
| **Busca** | Por item específico | Por conceito/tema |
| **Custo** | 120 embeddings | 1000+ embeddings |

---

## 💡 Exemplo: Busca Semântica

### Query: "What about drainage?"

```
1. Sistema cria embedding da query
   "What about drainage?" → [0.145, 0.789, ...]

2. Compara com TODOS os embeddings armazenados:

   CSV Items:
   ✅ "DRAINAGE SYSTEM - INSTALLATION - LS @ $45000" 
      (match score: 0.92)
   ❌ "MOBILIZATION - LS @ $33950" 
      (match score: 0.12)

   PDF Chunks:
   ✅ "The drainage system includes underdrains 
       for stormwater management and includes..."
      (match score: 0.88)
   ✅ "Installation of underdrains per specifications..."
      (match score: 0.85)
   ✅ "Drainage requirements: depth 18 inches..."
      (match score: 0.79)

3. Retorna top 5 resultados (CSV + PDF combinados)
```

---

## 📊 Custo de Embeddings

### OpenAI text-embedding-3-small:
- **CSV**: 120 items × ~15 tokens = 1,800 tokens
- **PDF**: 1,847 chunks × ~150 tokens = 277,050 tokens
- **Total**: ~278,850 tokens

### Custo estimado:
```
$0.02 / 1M tokens
278,850 tokens → ~$0.0056
(menos de 1 centavo por sessão!)
```

---

## 🎯 Por que os dois?

**CSV:**
- ✅ Dados **estruturados**
- ✅ Preços precisos
- ✅ Comparações claras
- ✅ Poucos documentos → rápido

**PDF:**
- ✅ Contexto **detalhado**
- ✅ Especificações técnicas
- ✅ Requisitos do projeto
- ✅ Informações não-estruturadas

**Juntos:**
- ✅ Busca **abrangente**
- ✅ Respostas com **múltiplas fontes**
- ✅ Compreensão **completa** do projeto

---

## 📝 Exemplo de Resposta com Ambos

**User Query:** "What's the cost of drainage and how is it installed?"

**Resposta incluindo:**
```
📊 FROM CSV:
DRAINAGE SYSTEM - INSTALLATION - LS @ $45,000.00

📄 FROM PDF:
"Installation requirements include...
The drainage system must include underdrains...
Maximum depth 18 inches per specifications..."

✅ Resposta integra dados estruturados + contexto técnico
```

---

## 🔧 Como Funciona Internamente

### 1. Indexação (primeiro load):

```python
# CSV
for item in csv_items:
    text = f"{item.description} - {item.unit} @ ${item.price}"
    embedding = openai.embed(text)  # 1 API call por item
    vector_store.insert(embedding, text, metadata)

# PDF
for chunk in pdf_chunks:
    embedding = openai.embed(chunk)  # 1 API call por chunk
    vector_store.insert(embedding, chunk, metadata)
```

### 2. Busca (quando usuário pergunta):

```python
query = "What about drainage?"
query_embedding = openai.embed(query)  # 1 API call

# Busca vetorial (LOCAL, sem API):
results = vector_store.search(query_embedding, limit=5)
# Retorna top 5 matches de CSV + PDF
```

---

## 📈 Fluxo Completo

```
┌─ CSV (120 items)
│   ├─ Item 1 → Embedding → Storage
│   ├─ Item 2 → Embedding → Storage
│   └─ Item N → Embedding → Storage
│
├─ PDF (1847 chunks)
│   ├─ Chunk 1 → Embedding → Storage
│   ├─ Chunk 2 → Embedding → Storage
│   └─ Chunk N → Embedding → Storage
│
├─ User Query
│   └─ "What about drainage?"
│       → Embedding (1 API call)
│       → Vector Search (LOCAL)
│       → Results from CSV + PDF combined
│
└─ Agent Response
    └─ "Based on CSV: cost is $45k"
       "Based on PDF: installation requires..."
```

---

## ✅ Resumo

| Documento | Embedado? | Como? | Quantidade |
|-----------|-----------|-------|-----------|
| **CSV** | ✅ Sim | Item por item | 120 |
| **PDF** | ✅ Sim | Chunk por chunk | 1847 |
| **Total** | ✅ Sim | Ambos combinados | ~2000 |

**Resultado:** Sistema consegue buscar em ~2000 documentos simultaneamente com busca semântica! 🚀

---

## 💰 Otimização

Se quiser **reduzir custos**:

```python
# Em run_agent.py, mude para:
use_mock = True  # Forçar mock embeddings (grátis)

# Resultado:
# ✅ Busca ainda funciona (qualidade reduzida)
# ✅ Sem custo de API
# ❌ Menos preciso semanticamente
```

Mas com as suas API keys configuradas, o sistema usa **REAL embeddings** automaticamente! ✨
