# Construction Estimating Multi-Modal Agent

**Test Type**: Senior Engineer Take-Home  
**Duration**: ~3-4 hours  
**Evaluation Focus**: Architecture decisions, data handling robustness, query quality, outlier detection

## Quality Standards (Non-Negotiable)

### Architecture Patterns

#### Strategy Pattern (CSV Parsers)
- Auto-detect schema from CSV (no hardcoded columns)
- Adapt to missing fields, renamed columns, new formats
- Fallback: skip unknown columns, log warnings
- **How**: `CSVParser.infer_schema() → parse() → validate()`

#### Factory Pattern (Data Loading)
- `DataLoader.load(file_path)` auto-detects format (CSV/PDF/JSON)
- Returns normalized data model (Project, BidItem, etc)
- **How**: Check file extension/MIME type → dispatch to loader

#### Repository Pattern (Vector Store)
- Abstract backend (SQLite now, Pinecone/Weaviate later)
- `VectorStore.search()`, `VectorStore.insert()`, `VectorStore.delete()`
- **How**: Interface in `vectorstore/storage.py`, implementations swappable

#### Tool-Use (Agent Interfaces)
- Tools are Pydantic models with examples
- Agent (Claude) calls tools programmatically
- Tools compose: outlier detection + bidder comparison in one query
- **How**: `agent/tools.py` defines structured inputs/outputs

### Data Handling (Messy-First)

**CSV Parsing**:
- ✅ Column name variations (ENG_EST_UNIT_PR vs eng_est_unit_pr vs estimate_price)
- ✅ Missing columns (don't assume all columns exist)
- ✅ Empty cells (handle gracefully, not crash)
- ✅ Unexpected formats (quantities as "248.0" or "248" or "248 units")
- ✅ Multiple projects in one file (group by PROJ_ID)

**PDF Extraction**:
- ✅ Text-native PDFs (PyPDF2)
- ✅ Scanned images (pytesseract OCR with fallback)
- ✅ Mixed content (text + images on same page)
- ✅ Messy OCR output (partial words, line breaks mid-word)
- ✅ Gracefully degrade (extract what we can, note what we couldn't)

**Data Validation**:
- Check data types (qty should be numeric, not string)
- Flag inconsistencies (unit price 10x others for same item = outlier, not error)
- Track missing data (don't drop rows, mark as "incomplete")

### Query Quality

**Accurate**: Answer comes from data, not hallucination
- Search embeddings for context
- Cite which file/row the answer came from
- Say "I don't have that data" if not present

**Composable**: Agent can chain queries
- "Top 5 expensive items" (requires sort + limit)
- "Items with outlier prices" (requires outlier detection + bidder comparison)
- "Summarize drainage requirements from plans" (requires PDF search + extraction)

**Grounded**: Show work
- "Item X has median price $Y (from N bidders)"
- "Outlier: Item Z has price $W, which is 3.2σ above mean"

### Outlier Detection

**Methods**:
- Z-score: (value - mean) / stddev, flag if |z| > 2.0 (configurable)
- IQR: flag if value < Q1 - 1.5*IQR or > Q3 + 1.5*IQR
- Context: outliers are *interesting*, not *errors*

**Implementation**:
- `analysis/outliers.py` exports `detect_outliers(values, method="zscore", sensitivity=2.0)`
- Returns: outlier indices, z-scores, context ("2.1σ above mean")
- Handle edge cases: all values equal, single value, <3 values

### Code Quality

#### High Cohesion
- All CSV parsing code → `data/parsers.py`
- All outlier logic → `analysis/outliers.py`
- Methods do one thing well

#### Low Coupling
- `data/loaders.py` → `data/parsers.py` → `data/models.py` (one-way)
- `vectorstore/` doesn't know about `agent/`
- Dependency injection: pass dependencies, don't instantiate internally

#### SOLID Principles
- **S**ingle Responsibility: `OutlierDetector` only detects outliers
- **O**pen/Closed: Add new parsers without modifying `DataLoader`
- **L**iskov Substitution: All parsers implement `BaseParser` interface
- **I**nterface Segregation: Small interfaces (e.g., `Embedder` not "DoEverything")
- **D**ependency Inversion: Depend on abstractions, not concrete implementations

#### Naming
- Classes: `CSVParser`, `OutlierDetector`, `SemanticSearcher` (noun, action verb)
- Functions: `parse_csv()`, `detect_outliers()`, `search_embeddings()` (verb_noun)
- Variables: `bid_items`, `outlier_indices`, `embedding_vector` (clear plurals, clear types)

### Testing (>80% coverage)

**Unit Tests**:
- `test_parsers.py`: CSV with missing columns, PDF with OCR fallback
- `test_outliers.py`: Z-score edge cases (empty, single value, all equal)
- `test_embeddings.py`: Mock OpenAI API (don't call real endpoint in tests)

**Integration Tests**:
- `test_agent.py`: End-to-end query (upload → parse → embed → agent response)
- `test_retrieval.py`: Semantic search returns relevant chunks

**Fixtures**:
- Sample CSV with edge cases (missing columns, empty cells)
- Sample PDF (scanned image or text-native)
- Expected outputs for reproducibility

### Security (OWASP)

- ✅ **Input validation**: File size limit (10MB), extension check, CSV format validation
- ✅ **Injection prevention**: Parameterize all LLM prompts (no f-strings for user input)
- ✅ **Error handling**: Catch exceptions, return generic message, log full error internally
- ✅ **API keys**: Store in .env, never commit to git
- ✅ **Dependencies**: Managed in pyproject.toml (modern PEP 517)
- ✅ **Logging**: No sensitive data (don't log full CSV rows, API keys, etc)

## Architecture Decisions (Why/How)

### Why Python?
- Rich ecosystem (pandas, scikit-learn, fastapi)
- Fast iteration (matches 3-4 hour expectation)
- Data transformation is idiomatic

### Why SQLite Vector Store (not Pinecone)?
- Local-only: no external dependencies
- <5 minute setup: pip install, no signup
- Inspectable: inspect vectors in SQLite browser
- Trade-off: Slower than Pinecone at scale, but fine for this test

### Why Claude API (not LangChain)?
- Native structured tool-use
- Composable: agent calls multiple tools in one response
- Cleaner: no abstraction overhead for this use case

### Why text-embedding-3-small (not large)?
- Fast enough: 1536 dimensions vs 3072
- Cheaper: 2x cost difference
- Good enough: semantic search on construction data is not super fine-grained

### Why Pydantic for Tools?
- Type-safe: agent can reason about inputs/outputs
- Serializable: convert to JSON for API
- Composable: chain tool outputs as inputs

## What We're NOT Doing

- ❌ No UI polish (CLI only)
- ❌ No Kubernetes/Docker (local only)
- ❌ No perfect OCR (graceful degradation)
- ❌ No 100% test coverage (>80% is good)
- ❌ No over-engineering (3 similar functions can stay as 3)

## What Separates Good from Great

**Good**: Parse files, embed, answer questions

**Great**: 
- Tools are composable (agent chains multiple in one response)
- Handles data variability (works with different CSV schemas)
- Outliers are insightful, not just flagged
- Architecture is extensible (add new parser type without changing agent)

## Development Workflow

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -e .              # Install project + dependencies
pip install -e ".[dev]"       # Include dev dependencies (pytest, etc)

# Configuration
cp .env.example .env          # Add your OpenAI/Anthropic keys

# Development
# Make changes → Run tests → Verify manually

# Testing
pytest tests/ -v --cov=src --cov-report=html

# Run agent (CLI)
python src/main.py analyze --file data/sample_bid_tabulation.csv

# Run agent (interactive)
python -m src.main analyze --file data/sample_bid_tabulation.csv
```

## Files to Create (Per Phase)

### Phase 1: Data Ingestion
- `src/data/models.py` - Pydantic models (Project, BidItem, etc)
- `src/data/parsers.py` - CSV schema inference + parsing
- `src/data/loaders.py` - File loader (CSV/PDF auto-detect)
- `src/data/validators.py` - Data quality checks

### Phase 2: Vector Store
- `src/vectorstore/embeddings.py` - OpenAI wrapper
- `src/vectorstore/storage.py` - SQLite storage
- `src/vectorstore/retrieval.py` - Search (semantic + keyword)

### Phase 3: Analysis
- `src/analysis/outliers.py` - Outlier detection
- `src/analysis/aggregations.py` - Stats, top-N, grouping
- `src/analysis/comparisons.py` - Bidder/item comparisons

### Phase 4: Agent
- `src/agent/tools.py` - Tool definitions (Pydantic)
- `src/agent/core.py` - Agent orchestrator (Claude SDK)
- `src/agent/prompts.py` - System prompt + examples

### Phase 5: Polish
- `src/main.py` - CLI entry point
- `tests/` - Full test suite
- `README.md` - Setup instructions

## Remember

1. **Data variability is the test**: If your parser only works on this exact CSV, you failed.
2. **Tool-use separates great from good**: Spend time on composable tool definitions.
3. **Outliers are interesting**: Don't just flag them; explain why they're deviations.
4. **Show your work**: Agent responses should cite data sources.
5. **No over-engineering**: Good is better than perfect. Done is better than perfect.
