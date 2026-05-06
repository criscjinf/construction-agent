# Next Steps

## 🎯 Immediate (Next Session)

1. **Create project structure** (`/feature` or manual)
   - `mkdir -p src/{data,vectorstore,analysis,agent}`
   - `mkdir -p tests/{unit,integration,fixtures}`

2. **Phase 1: Data Models + CSV Parser**
   - [ ] `src/data/models.py`: Pydantic models (Project, BidItem, Bidder)
   - [ ] `src/data/parsers.py`: CSVParser with schema inference
   - [ ] `src/data/validators.py`: Data quality checks
   - [ ] `tests/unit/test_parsers.py`: Schema inference tests

3. **Test against sample_bid_tabulation.csv**
   - Load CSV
   - Infer schema (detect columns dynamically)
   - Parse all rows
   - Verify no errors on edge cases (missing cols, empty cells)

4. **Checkpoint**: Can parse CSV with variable schema ✓

## 🔄 Short Term (Same Session)

5. **Phase 2: Vector Store**
   - [ ] `src/vectorstore/embeddings.py`: OpenAI wrapper
   - [ ] `src/vectorstore/storage.py`: SQLite storage + search
   - [ ] `tests/integration/test_retrieval.py`: Search tests
   
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
