# 🧠 How Embeddings Work - CSV vs PDF

## 📊 CSV - Item by Item

### Flow:

```
CSV (sample_bid_tabulation.csv)
        ↓
   Parser (auto-detects columns)
        ↓
   For each item:
   ┌─────────────────────────────────────┐
   │ Item #1031000                       │
   │ "MOBILIZATION - LS @ $33950.00"     │
   │                                      │
   │ ↓ EMBEDDING (OpenAI)                │
   │                                      │
   │ [0.234, -0.156, 0.789, ...]        │
   │ (1536 dimensions)                   │
   │                                      │
   │ ↓ Store in Vector Store             │
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

### Result:
- ✅ **120 documents** indexed
- ✅ Each item is a **short string**
- ✅ Each string has a **separate embedding**
- ✅ Semantic search works on individual items

---

## 📄 PDF - Divided into Chunks

### Flow:

```
PDF (plans.pdf - 21.6MB)
        ↓
   Text Extraction (PyPDF2 or OCR)
   Result: 193,846 characters
        ↓
   Chunk Division (size ~500 chars)
        ↓
   For each chunk:
   ┌──────────────────────────────────────┐
   │ Chunk #0                             │
   │ "MoDOT PROJECT NO. 21-082A-3...     │
   │ NEVADA MUNICIPAL AIRPORT (NVD)...   │
   │ Base Bid Reconstruct Runway..."     │
   │                                       │
   │ ↓ EMBEDDING (OpenAI)                 │
   │                                       │
   │ [0.512, -0.234, 0.101, ...]         │
   │ (1536 dimensions)                    │
   │                                       │
   │ ↓ Store in Vector Store              │
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

### Result:
- ✅ **~1847 chunks** indexed
- ✅ Each chunk is a **text block** (~500 characters)
- ✅ Each chunk has a **separate embedding**
- ✅ Semantic search works on document sections

---

## 🔍 Key Differences

| Aspect | CSV | PDF |
|--------|-----|-----|
| **What gets embedded** | Each item (description + price) | Text chunks (paragraphs) |
| **Number of docs** | Few (120 items) | Many (1000+) |
| **Size of each doc** | Small (50-100 chars) | Medium (500 chars) |
| **Structure** | Structured (columns) | Unstructured (free text) |
| **Search** | For specific item | For concept/theme |
| **Cost** | 120 embeddings | 1000+ embeddings |

---

## 💡 Example: Semantic Search

### Query: "What about drainage?"

```
1. System creates embedding of query
   "What about drainage?" → [0.145, 0.789, ...]

2. Compares with ALL stored embeddings:

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

3. Returns top 5 results (CSV + PDF combined)
```

---

## 📊 Embedding Costs

### OpenAI text-embedding-3-small:
- **CSV**: 120 items × ~15 tokens = 1,800 tokens
- **PDF**: 1,847 chunks × ~150 tokens = 277,050 tokens
- **Total**: ~278,850 tokens

### Estimated cost:
```
$0.02 / 1M tokens
278,850 tokens → ~$0.0056
(less than 1 cent per session!)
```

---

## 🎯 Why Both?

**CSV:**
- ✅ **Structured** data
- ✅ Accurate prices
- ✅ Clear comparisons
- ✅ Few documents → fast

**PDF:**
- ✅ **Detailed** context
- ✅ Technical specifications
- ✅ Project requirements
- ✅ Unstructured information

**Together:**
- ✅ **Comprehensive** search
- ✅ Answers with **multiple sources**
- ✅ **Complete** project understanding

---

## 📝 Example Response with Both

**User Query:** "What's the cost of drainage and how is it installed?"

**Response includes:**
```
📊 FROM CSV:
DRAINAGE SYSTEM - INSTALLATION - LS @ $45,000.00

📄 FROM PDF:
"Installation requirements include...
The drainage system must include underdrains...
Maximum depth 18 inches per specifications..."

✅ Response integrates structured data + technical context
```

---

## 🔧 How It Works Internally

### 1. Indexing (first load):

```python
# CSV
for item in csv_items:
    text = f"{item.description} - {item.unit} @ ${item.price}"
    embedding = openai.embed(text)  # 1 API call per item
    vector_store.insert(embedding, text, metadata)

# PDF
for chunk in pdf_chunks:
    embedding = openai.embed(chunk)  # 1 API call per chunk
    vector_store.insert(embedding, chunk, metadata)
```

### 2. Search (when user asks):

```python
query = "What about drainage?"
query_embedding = openai.embed(query)  # 1 API call

# Vector search (LOCAL, no API):
results = vector_store.search(query_embedding, limit=5)
# Returns top 5 matches from CSV + PDF
```

---

## 📈 Complete Flow

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

## ✅ Summary

| Document | Embedded? | How? | Quantity |
|----------|-----------|------|----------|
| **CSV** | ✅ Yes | Item by item | 120 |
| **PDF** | ✅ Yes | Chunk by chunk | 1847 |
| **Total** | ✅ Yes | Both combined | ~2000 |

**Result:** System can search ~2000 documents simultaneously with semantic search! 🚀

---

## 💰 Optimization

To **reduce costs**:

```python
# In run_agent.py, change to:
use_mock = True  # Force mock embeddings (free)

# Result:
# ✅ Search still works (reduced quality)
# ✅ No API costs
# ❌ Less semantically accurate
```

But with your API keys configured, the system automatically uses **REAL embeddings**! ✨
