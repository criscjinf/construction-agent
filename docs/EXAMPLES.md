# 📋 Log Examples - Understand Each Message

## 1️⃣ Normal Initialization (LOG_LEVEL=INFO)

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
   • CSV items: [count]
   • PDF chunks: 0
   • Total: [count]
```

**Analysis:**
- ✅ Documents loaded
- ✅ CSV indexed correctly
- ✅ No PDFs found (normal)

---

## 2️⃣ Initialization with LOG_LEVEL=DEBUG

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
```

**What this means:**
- System initialized in DEBUG mode
- Created temporary database
- Vector store ready
- DocumentLoader initialized
- Starting indexing process

---

## 3️⃣ Successful CSV Indexing

```
2026-05-08 14:32:46 | DEBUG   | document_loader      | load_and_index_csv   | Processing: sample_bid_tabulation.csv
2026-05-08 14:32:46 | DEBUG   | loaders              | load                 | Auto-detected format: CSV
2026-05-08 14:32:46 | DEBUG   | parsers              | parse                | Inferring schema from CSV...
2026-05-08 14:32:46 | DEBUG   | parsers              | infer_schema         | Found columns: PROJ_ID, ITEM_NO, ITEM_DESC, QUANTITY, UNIT_PRICE, BIDDER
2026-05-08 14:32:47 | DEBUG   | document_loader      | load_and_index_csv   | Embedded all items
2026-05-08 14:32:47 | INFO    | run_agent            | main                 | ✅ CSV indexed: sample_bid_tabulation.csv
```

**What this means:**
- CSV detected automatically ✅
- Schema inferred from columns ✅
- All items embedded successfully ✅

---

## 4️⃣ Agent Ready

```
==========================================================================================
  🤖 INITIALIZING AGENT
==========================================================================================

✅ Agent ready with 4 tools
   • Search (CSV + PDF)
   • Top Items
   • Outlier Detection
   • Bidder Comparison
```

Agent is initialized with all tools available.

---

## 5️⃣ User Query Example

```
==========================================================================================
  💬 ANALYSIS MODE
==========================================================================================

📍 You: What are the top 5 most expensive items?

🤖 Claude is analyzing...

------------------------------------------------------------------------------------------
Here are the **Top 5 Most Expensive Bid Items**:

1. **MOBILIZATION** - LS
   - Median Price: $33,950.00
   - Price Range: $26,500 - $40,000
   - Variance: $13,500 (50.9%)

2. **EVALUATION OF PAVEMENT MARKING** - LS
   - Median Price: $35,000.00
   - Price Range: $30,000 - $40,000
   - Variance: $10,000 (28.6%)

3. **TRAFFIC CONTROL** - LF
   - Median Price: $28,400.00
   - From N = 4 bidders
   - Estimated Total: $71,000,000

[Additional items...]

**Insights:**
- Item MOBILIZATION shows high price variance across bidders
- EVALUATION requires further analysis for cost drivers
------------------------------------------------------------------------------------------

📍 You: Are there any pricing anomalies?

🤖 Claude is analyzing...

------------------------------------------------------------------------------------------
**Pricing Anomalies Detected:**

📈 **Outliers (Z-Score > 2.0):**

1. **Item 1040000 - TRAFFIC CONTROL**
   - Bidder: Company_C
   - Outlier Price: $18,750.00
   - Expected Price: $15,500.00 (median)
   - Z-Score: 2.1σ (statistically significant)
   - Issue: 21% above median → investigate cost drivers

2. **Item 2033000 - BORROW EXCAVATION**
   - Bidder: Company_B
   - Outlier Price: $2,450.00
   - Expected Price: $850.00 (median)
   - Z-Score: 3.2σ (highly significant!)
   - Issue: 188% above median → likely data error or special requirements

**Recommendations:**
- Contact Company_C for TRAFFIC CONTROL pricing explanation
- Verify Company_B EXCAVATION quote (possible data entry error)
------------------------------------------------------------------------------------------

📍 You: quit

👋 Goodbye!
```

---

## 6️⃣ Error Handling

### Missing File:
```
❌ File not found: /path/to/nonexistent.csv
📂 Please provide a valid file path
```

### Invalid Format:
```
❌ Invalid format: '.xlsx'
   Supported: .csv, .pdf
```

### File Too Large:
```
❌ File too large: 150.5MB (max 100MB)
```

### API Credits Exhausted:
```
⚠️  API Credits/Quota Exceeded

Using mock embeddings - search may be less accurate.
```

---

## 7️⃣ Complete Session Log

```bash
$ LOG_LEVEL=DEBUG python3 scripts/run_agent.py

==========================================================================================
  🤖 CONSTRUCTION ESTIMATING AGENT
==========================================================================================

[Document selection and loading...]

==========================================================================================
  📊 INDEXING DOCUMENTS
==========================================================================================

✅ Indexing complete:
   • CSV items: [count]
   • PDF chunks: [count]
   • Total: [combined count]

==========================================================================================
  🤖 INITIALIZING AGENT
==========================================================================================

✅ Agent ready with 4 tools

==========================================================================================
  💬 ANALYSIS MODE
==========================================================================================

📍 You: What are the top 3 items?

🤖 Claude is analyzing...

[Claude response with data]

📍 You: What about drainage?

🤖 Claude is analyzing...

[Claude response with PDF and CSV data combined]

📍 You: quit

👋 Goodbye!
```

---

## Key Takeaways

✅ **SUCCESS indicators:**
- `✅ Loaded X documents`
- `✅ Agent ready with 4 tools`
- `✅ CSV indexed: X items`
- `✅ PDF indexed: X chunks`

⚠️ **WARNING indicators:**
- `⚠️ File not found`
- `⚠️ OCR unavailable`
- `⚠️ API Credits/Quota`

❌ **ERROR indicators:**
- `❌ Invalid format`
- `❌ File too large`
- `❌ Error loading`

📍 **User interaction indicators:**
- `📍 You:` = User question
- `🤖 Claude is analyzing...` = Processing
- `---------` = Response delimiter

---

**See `docs/DEBUGGING.md` for more detailed log interpretation.**
