# Next Steps

## ✅ Completed

1. ✓ **Create project structure**
   - ✓ `mkdir -p src/{data,vectorstore,analysis,agent}`
   - ✓ `mkdir -p tests/{unit,integration,fixtures}`

2. ✓ **Phase 1: Data Models + CSV Parser**
   - ✓ `src/data/models.py`: Pydantic models (Project, BidItem, Bidder, PDFContent)
   - ✓ `src/data/parsers.py`: CSVParser with schema inference
   - ✓ `src/data/loaders.py`: DataLoader factory
   - ✓ `src/data/validators.py`: Data quality checks
   - ✓ `tests/unit/test_parsers.py`: 22 tests (schema inference, edge cases, integration)
   - ✓ `tests/unit/test_models.py`: 14 model tests
   - ✓ `tests/unit/test_validators.py`: 11 validator tests
   - ✓ `tests/fixtures/sample_data.py`: Test fixtures

3. ✓ **Test against sample_bid_tabulation.csv**
   - ✓ Load CSV (auto-detected all columns)
   - ✓ Infer schema (handles missing/renamed columns)
   - ✓ Parse all rows without errors
   - ✓ Verify edge cases (empty cells, multiple projects, inconsistent types)

4. ✓ **Checkpoint**: Can parse CSV with variable schema

**Metrics**: 47 tests passing | 89% coverage | Real data parsing ✓

## ✅ Completed (Phase 2)

5. ✓ **Phase 2: Vector Store**
   - ✓ `src/vectorstore/embeddings.py`: OpenAI wrapper + MockEmbeddingClient
   - ✓ `src/vectorstore/storage.py`: SQLiteVectorStore (CRUD + similarity)
   - ✓ `src/vectorstore/retrieval.py`: HybridRetriever (semantic + keyword)
   - ✓ `tests/unit/test_embeddings.py`: 9 tests (determinism, batch)
   - ✓ `tests/integration/test_vectorstore.py`: 13 tests (CRUD, search, metadata)
   - ✓ `tests/integration/test_retrieval.py`: 12 tests (hybrid, weights)

**Metrics**: 34 new tests passing | 81 total tests | 0 regressions

## 🎯 Immediate Next (Phase 3)

6. **Phase 3: Analysis Tools** ← START HERE
   - [ ] `src/analysis/outliers.py`: Z-score + IQR detection
   - [ ] `src/analysis/aggregations.py`: Top items, statistics, summaries
   - [ ] `src/analysis/comparisons.py`: Bidder/item comparisons
   - [ ] `tests/unit/test_analysis.py`: Edge case tests (all equal, single value, etc)
   
   **Time**: ~35 min | **Success**: Detect outliers, compute stats, enable agent queries
   
6. **Phase 3: Analysis Tools**
   - [ ] `src/analysis/outliers.py`: Z-score + IQR
   - [ ] `src/analysis/aggregations.py`: Top items, stats
   - [ ] `tests/unit/test_outliers.py`: Edge case tests

7. **Phase 4: Agent + Tools**
   - [ ] `src/agent/tools.py`: Tool definitions (Pydantic models)
   - [ ] `src/agent/core.py`: Agent orchestrator (Claude SDK)
   - [ ] `src/agent/prompts.py`: System prompt + examples

8. **Phase 5: Polish**
   - [ ] `src/main.py`: CLI entry point
   - [ ] `README.md`: Setup instructions (must be <5min from clone)
   - [ ] Full test suite + coverage report
   - [ ] `/security` audit

## 📋 Example Queries to Test (End-to-End)

Once agent is running, verify it handles:

```
1. "What are the top 5 most expensive bid items?"
   → Uses aggregations.top_items() + search_embeddings()

2. "Are there any items with unit prices that deviate significantly?"
   → Uses outliers.detect_outliers() + bid data search

3. "What does the plan set say about drainage?"
   → Uses pdf search_embeddings() on PDF content

4. "Summarize the key quantities from the bid data"
   → Uses aggregations.summarize() + multiple searches

5. "Compare ASPHALT PAVING prices across bidders"
   → Uses comparisons.compare_bidders() with specific item
```

## 🎓 Evaluation Criteria (From Test Brief)

Before submission, verify:

- [ ] **Architecture**: Can swap SQLite → Pinecone without changing agent
- [ ] **Data Handling**: Works with CSV missing columns, PDFs with OCR errors
- [ ] **Query Quality**: Agent cites sources ("per bidder X on line Y")
- [ ] **Outliers**: Detects >2σ deviations, explains why
- [ ] **Code Quality**: No over-engineering, high cohesion, low coupling
- [ ] **Tool-Use**: Tools are composable (agent chains multiple in one response)

## 🚀 Submission Checklist

Before pushing to GitHub:

- [ ] README.md includes:
  - Setup instructions (<5 min)
  - Example queries
  - Architecture decisions + rationale
  - What you'd change with more time
- [ ] Test suite passing (>80% coverage)
- [ ] `/security` audit passes
- [ ] `.env.example` in repo (keys not committed)
- [ ] `requirements.txt` with pinned versions
- [ ] Commit history is clean

## ⏱️ Time Budget

- Phase 1 (Data): 60 min
- Phase 2 (Vectors): 40 min
- Phase 3 (Analysis): 35 min
- Phase 4 (Agent): 45 min
- Phase 5 (Polish): 40 min
- **Total**: ~200 min (3.3 hours)

## 🎬 How to Continue

Run `/feature "Phase 1: Data models and CSV parser"` to start next phase with full context.

Or if continuing same session, run `/next` to see detailed next step.
