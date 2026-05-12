# 🚀 Quick Start - Construction Estimating Agent

## ⚡ TL;DR (30 seconds)

```bash
agent
# → Choose option 2 (Start analysis)
# → Ask questions
```

---

## 📋 Overview

The agent provides **a single command** that does everything:
- ✅ Upload CSV/PDF files
- ✅ Automatic indexing (embeddings)
- ✅ Semantic search
- ✅ Analysis with Claude

---

## 🎯 Complete Workflow

### **Option 1: Load from `data/` folder (RECOMMENDED)**

```bash
agent
```

Menu:
```
Options:
  1. Upload a file (auto-detect CSV/PDF)
  2. Start analysis

👉 Choose (1-2): 2
```

Result:
```
✅ Documents ready for indexing: 4
📊 Indexing documents...
   ✅ CSV indexed: 342 items (batch embedded)
   ✅ PDF indexed: 127 chunks (batch embedded)
✅ Indexing complete: 469 total
🤖 Agent ready with 4 tools
```

### **Option 2: Upload new files**

```bash
agent
```

Menu:
```
Options:
  1. Upload a file (auto-detect CSV/PDF)
  2. Start analysis

👉 Choose (1-2): 1
📂 Enter file path: /path/to/your_file.csv
✅ Uploaded: your_file.csv
   Detected type: CSV
   ✅ CSV parsed: 2 projects

👉 Choose (1-2): 1
[Upload more files, or...]

👉 Choose (1-2): 2
[Start analysis]
```

### **Option 3: Use demo (automated)**

```bash
agent-demo
```

This automatically:
- Loads all files from `data/`
- Indexes them with batch embeddings
- Runs 3 example queries
- Cleans up and exits

---

## 💬 Asking Questions

After choosing an option, you interact like this:

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

## 📊 Supported Formats

### CSV (Bid Tabulation)
- ✅ Any column structure
- ✅ Column names can vary (UNIT_PRICE, unit_price, estimate_price, etc)
- ✅ Empty fields are tolerated
- ✅ Multiple projects in one file

**Expected example:**
```
PROJ_ID, ITEM_NO, ITEM_DESC, QUANTITY, UNIT_PRICE, BIDDER
P001, 1031000, MOBILIZATION, 1, 33950.00, Company A
P001, 1040000, TRAFFIC CONTROL, 2500, 15.50, Company A
```

### PDF (Plans & Specifications)
- ✅ PDFs with native text (PyPDF2)
- ✅ Scanned PDFs with OCR
- ✅ Up to 100MB per file
- ✅ Multiple documents
- ✅ Any content (drawings, tables, text)

---

## 🎯 Example Questions

### CSV Analysis:
```
"What are the top 5 most expensive items?"
"Are there any pricing anomalies?"
"Compare bidder prices on MOBILIZATION"
"Which items have highest price variance?"
"Items with the most bidder competition"
```

### PDF Analysis:
```
"What does the plan say about drainage?"
"What are the specification requirements?"
"Find information about pavement marking"
"Summarize the key project details"
"What utilities are mentioned?"
```

### Semantic Search:
```
"Search for asphalt items"
"Find all traffic control specifications"
"What's mentioned about excavation?"
```

---

## ⚡ Commands inside the program

| Command | Effect |
|---------|--------|
| `help` | Show help and examples |
| `examples` | List suggested questions |
| `quit` | Exit the program |

---

## 🚀 Available Commands

| Command | Purpose | When to Use |
|---------|---------|------------|
| **`agent`** | Interactive: upload files or load from data/ | **Daily use** |
| **`agent-demo`** | Automated demo with example queries | Quick test, no interaction |

Both commands are available after `pip install -e .`

Or run directly:
```bash
python3 src/main.py   # Interactive
python3 src/demo.py   # Demo
```

---

## 📁 File Organization

```
project/
├── src/
│   ├── main.py          ⭐ Entry point (interactive agent)
│   ├── demo.py          (automated demo)
│   ├── data/            (parsers, loaders, indexers)
│   ├── vectorstore/     (embeddings, storage, retrieval)
│   ├── agent/           (Claude tools & agent executor)
│   └── analysis/        (outliers, comparisons, aggregations)
├── data/                (put your CSVs and PDFs here)
│   ├── sample_bid_tabulation.csv
│   ├── plans.pdf
│   └── ...
├── tests/               (130+ tests)
│   ├── unit/
│   └── integration/
└── docs/
    ├── QUICK_START.md
    ├── EMBEDDINGS.md
    └── ...
```

---

## ❓ FAQ

**Q: Do I need credits to use this?**
A: Not required. Upload/indexing are local. Credits only needed for real embeddings (not mock).

**Q: Are my data saved?**
A: No. Each session uses a temporary database that is deleted on exit. For persistence, copy files to `data/`.

**Q: How many documents can I use?**
A: No technical limit (up to 100MB per file).

**Q: My CSV has a different structure?**
A: No problem! System auto-detects columns.

**Q: Can I use scanned PDFs?**
A: Yes! Automatic OCR is applied.

**Q: How do I add data permanently?**
A: Copy CSVs/PDFs to the `data/` folder and load with option 2 or 3.

---

## 🔧 Troubleshooting

### Error: "agent: command not found"
```bash
# Make sure project is installed
pip install -e .
```

### Error: "File not found"
```bash
# Use absolute path when uploading
/home/your_user/Documents/file.csv
# or relative from project root
data/your_file.csv
```

### Error: "Invalid format"
```
❌ Received: .xlsx, .txt, .doc
✅ Supported: .csv, .pdf
```

### Error: "File too large"
```
Limit: 100MB per file
Solution: Split into smaller files
```

### Agent responses are slow
```
Normal! First query takes ~5-10s (embeddings generation).
Subsequent queries are instant (cache hit).
```

### API Credits Exhausted
```
If using real embeddings and credits run out:
✅ System auto-detects and switches to mock embeddings
✅ Search continues working (less accurate)
```

---

## 🎬 Next Steps

1. **First time (fastest way):**
   ```bash
   agent
   # When prompted:
   # Choose: 2 (Start analysis)
   ```

2. **With your own data:**
   ```bash
   cp your_file.csv data/
   agent
   # Choose: 2
   ```

3. **Upload files without saving:**
   ```bash
   agent
   # Choose: 1
   # Enter file path
   # Repeat for multiple files
   # Then choose: 2 (Start analysis)
   ```

4. **Quick automated demo:**
   ```bash
   agent-demo
   ```

---

## 📚 Additional Documentation

- `DEBUGGING.md` — Enable detailed logs
- `EMBEDDINGS.md` — How embeddings and search work
- `SECURITY.md` — Security audit
- `EXAMPLES.md` — Detailed log outputs

---

## 🚀 Optimization Notes

The agent uses **batch embeddings** for faster indexing:
- ✅ 5-10x speedup on document indexing
- ✅ Processes up to 1000 documents per API call
- ✅ Automatic fallback to mock embeddings if credits exhausted

See `docs/EMBEDDINGS.md` for technical details.

---

**Ready to get started?**
```bash
agent
```
